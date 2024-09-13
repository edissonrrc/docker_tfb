import os
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from datetime import timedelta

# Ruta al archivo CSV de datos limpios
csv_file_path = '/opt/airflow/data/csv/datos_limpios.csv'

# Definir los argumentos predeterminados para el DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG
dag = DAG(
    'Carga',
    default_args=default_args,
    description='DAG para cargar el archivo datos limpios en una tabla de PostgreSQL',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
)

# Función para crear la tabla en PostgreSQL
def crear_tabla_postgres():
    # Obtener la conexión a PostgreSQL
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # Sentencia SQL para crear la tabla
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS propiedades (
        key SERIAL PRIMARY KEY,
        captura DATE,
        precio INTEGER,
        precio_m² INTEGER
        agencia VARCHAR(255),
        aseos NUMERIC,
        zona VARCHAR(255),
        superficie INTEGER,
        habitaciones INTEGER,
        gastos INTEGER,
        extras TEXT
    );
    '''

    # Ejecutar la creación de la tabla
    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()

# Función para cargar los datos del CSV a la tabla de PostgreSQL
def cargar_datos_csv_a_postgres():
    # Leer el archivo CSV
    df = pd.read_csv(csv_file_path)

    # Convertir tipos de datos a nativos de Python (int, float, str)
    df = df.astype({
        'precio': 'int',
        'precio_m²': 'int',
        'aseos': 'float',
        'habitaciones': 'int',
        'gastos': 'int',
        'superficie': 'int',
    })

    # Obtener la conexión a PostgreSQL
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # Insertar los datos en la tabla
    for index, row in df.iterrows():
        insert_sql = '''
        INSERT INTO docker_tfb (captura, precio, precio_m², agencia, aseos, zona, superficie, habitaciones, gastos, extras)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        cursor.execute(insert_sql, (
            row['captura'],
            row['precio'],
            row['precio_m²'],
            row['agencia'],
            row['aseos'],
            row['zona'],
            row['superficie'],
            row['habitaciones'],
            row['gastos'],
            row['extras']
        ))

    # Confirmar los cambios en la base de datos
    conn.commit()
    cursor.close()
    conn.close()

# Definir las tareas del DAG
crear_tabla_task = PythonOperator(
    task_id='crear_tabla_postgres',
    python_callable=crear_tabla_postgres,
    dag=dag,
)

cargar_datos_task = PythonOperator(
    task_id='cargar_datos_csv_a_postgres',
    python_callable=cargar_datos_csv_a_postgres,
    dag=dag,
)

# Definir la secuencia de tareas
crear_tabla_task >> cargar_datos_task
