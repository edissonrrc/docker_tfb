from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

# Definir el directorio raíz y el script de generación de Gantt
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_path = os.path.join(root_dir, 'scripts', 'Generar_gantt_script.py')  # Ruta al script

# Definición del DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}

with DAG(dag_id='Crear_GANTT', default_args=default_args, description= 'DAG de creación de un fichero PNG con la planificación de los hitos, fases y fechas el proyecto', schedule_interval=None) as dag:

    ejecutar_script_gantt = BashOperator(
        task_id='ejecutar_script_gantt',
        bash_command=f'python3 {script_path}'  # Ejecutar el script Python
    )

