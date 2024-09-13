import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Agregar la ruta de la carpeta scripts al sys.path
scripts_path = '/opt/airflow/scripts'
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Importar las funciones de extracción de los 4 scripts
from Fazwaz_Extract import procesar_archivos_fazwaz
from Mitula_Extract import convertir_txt_a_csv as procesar_archivos_mitula
from Properati_Extract import procesar_archivos_txt_a_csv as procesar_archivos_properati
from Remax_Extract import convertir_txt_a_csv as procesar_archivos_remax

# Argumentos por defecto para el DAG
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
    'Extract',
    default_args=default_args,
    description='DAG para extraer datos de archivos HTML y convertirlos a CSV de diferentes fuentes',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    catchup=False,
)

# Definir las tareas para cada fuente de datos

# Tarea para procesar los archivos de Fazwaz
extract_fazwaz_task = PythonOperator(
    task_id='extraer_datos_fazwaz',
    python_callable=procesar_archivos_fazwaz,
    op_kwargs={
        'carpeta_origen': '/opt/airflow/data/output',  # Carpeta donde están los archivos raw de Fazwaz
        'carpeta_salida': '/opt/airflow/data/csv'      # Carpeta donde se guardarán los archivos CSV procesados
    },
    dag=dag,
)

# Tarea para procesar los archivos de Mitula
extract_mitula_task = PythonOperator(
    task_id='extraer_datos_mitula',
    python_callable=procesar_archivos_mitula,
    op_kwargs={
        'carpeta_origen': '/opt/airflow/data/output',  # Carpeta donde están los archivos raw de Mitula
        'carpeta_salida': '/opt/airflow/data/csv'      # Carpeta donde se guardarán los archivos CSV procesados
    },
    dag=dag,
)

# Tarea para procesar los archivos de Properati
extract_properati_task = PythonOperator(
    task_id='extraer_datos_properati',
    python_callable=procesar_archivos_properati,
    op_kwargs={
        'carpeta_origen': '/opt/airflow/data/output',  # Carpeta donde están los archivos raw de Properati
        'carpeta_salida': '/opt/airflow/data/csv'      # Carpeta donde se guardarán los archivos CSV procesados
    },
    dag=dag,
)

# Tarea para procesar los archivos de Remax
extract_remax_task = PythonOperator(
    task_id='extraer_datos_remax',
    python_callable=procesar_archivos_remax,
    op_kwargs={
        'carpeta_origen': '/opt/airflow/data/output',  # Carpeta donde están los archivos raw de Remax
        'carpeta_salida': '/opt/airflow/data/csv'      # Carpeta donde se guardarán los archivos CSV procesados
    },
    dag=dag,
)

# Dependencias entre las tareas
extract_fazwaz_task >> extract_mitula_task >> extract_properati_task >> extract_remax_task
