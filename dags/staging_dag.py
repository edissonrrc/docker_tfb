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

# Importar las funciones de scraping
from Fazwaz_Scraping import extraer_html_propiedades as Fazwaz_Scraping
from Mitula_Scraping import extraer_html_propiedades as Mitula_Scraping
from Properati_Scraping import extraer_html_propiedades as Properati_Scraping
from Remax_Scraping import extraer_html_propiedades as Remax_Scraping

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'Staging',
    default_args=default_args,
    description='DAG de scraping para diferentes fuentes de datos inmobiliarios',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    catchup=False,
)

# Funciones para cada fuente de datos
scraping_fazwaz_task = PythonOperator(
    task_id='Fazwaz_Scraping',
    python_callable=Fazwaz_Scraping,
    op_kwargs={'ciudad': 'pichincha/quito', 'paginas': 2},  # Asegúrate de pasar los argumentos correctos
    dag=dag,
)

scraping_mitula_task = PythonOperator(
    task_id='Mitula_Scraping',
    python_callable=Mitula_Scraping,
    op_kwargs={'ciudad': 'pichincha/quito', 'paginas': 2},
    dag=dag,
)

scraping_properati_task = PythonOperator(
    task_id='Properati_Scraping',
    python_callable=Properati_Scraping,
    op_kwargs={'ciudad': 'quito', 'paginas': 2},
    dag=dag,
)

scraping_remax_task = PythonOperator(
    task_id='Remax_Scraping',
    python_callable=Remax_Scraping,
    op_kwargs={'ciudad': 'quito', 'paginas': 2},
    dag=dag,
)

# Dependencias entre las tareas
scraping_fazwaz_task >> scraping_mitula_task >> scraping_properati_task >> scraping_remax_task
