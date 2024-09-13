import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Agregar la ruta del script transformador.py al sistema
scripts_path = '/opt/airflow/scripts'
if scripts_path not in os.sys.path:
    os.sys.path.insert(0, scripts_path)

# Importar las funciones necesarias del archivo transformador.py
from Transformador import procesar_todas_inmobiliarias

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'Transform',
    default_args=default_args,
    description='DAG para limpiar y procesar datos inmobiliarios',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
)

# Función que envuelve la ejecución del proceso de transformación
def ejecutar_proceso_transformador():
    df_final = procesar_todas_inmobiliarias()
    print("Proceso completado correctamente")

# Definir la tarea de Airflow que ejecuta el transformador
transform_task = PythonOperator(
    task_id='run_transformador_script',
    python_callable=ejecutar_proceso_transformador,
    dag=dag,
)

transform_task
