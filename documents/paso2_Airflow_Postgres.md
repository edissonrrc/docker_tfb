## Documentación del Proyecto: Configuración de Airflow con PostgreSQL y Otras Herramientas
Esta documentación cubre todos los pasos seguidos hasta ahora para configurar y verificar un entorno de Airflow conectado a PostgreSQL, junto con otros servicios como Spark y Metabase. Este entorno está diseñado para ejecutar tareas de ETL y análisis de datos, como scraping, transformación de datos, y visualización.

## 1. Configuración Inicial
##    1.1. Preparación del Entorno
        - Directorio del Proyecto: El proyecto se configuró en un directorio llamado proyecto_tfb bajo ~/Descargas.
        - Estructura de Directorios:
            proyecto_tfb/
            ├── dags/                 	# Almacena los DAGs de Airflow
            ├── logs/                 	# Almacena los logs generados por Airflow
            ├── plugins/               	# Almacena los plugins de Airflow
            ├── data/
            │   ├── csv/               	# Archivos CSV de entrada
            │   ├── output/            	# Salida de datos procesados
            │   └── html/	       	# Html descargado para posterior captura de datos.
            ├── db_data/               	# Directorio de datos persistentes para PostgreSQL
            ├── metabase_data/         	# Directorio de datos para Metabase
            ├── .env                   	# Archivo de variables de entorno
            └── docker-compose.yml     	# Archivo de configuración de Docker Compose
  
##    1.2. Configuración del Archivo .env
    El archivo .env se utiliza para almacenar las variables de entorno necesarias para la configuración de PostgreSQL y Airflow. El contenido del archivo es el siguiente:
        POSTGRES_DB=tfb
        POSTGRES_USER=edi
        POSTGRES_PASSWORD=POSTGRES_PASSWORD**
        AIRFLOW_ADMIN_USER=admin
        AIRFLOW_ADMIN_PASSWORD=AIRFLOW_ADMIN_PASSWORD**
        AIRFLOW_ADMIN_EMAIL=edisson.reyes.data@gmail.com

## 2. Configuración de docker-compose.yml
Se creó un archivo docker-compose.yml para definir los servicios de Docker necesarios para el proyecto. Este archivo configura los servicios para PostgreSQL, Airflow (webserver y scheduler), Spark (master y worker), y Metabase.

version: '3'
services:
  postgres:
    image: postgres:13
    container_name: postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - ./db_data:/var/lib/postgresql/data
    networks:
      - airflow-network

  airflow-webserver:
    image: apache/airflow:2.7.0-python3.9
    container_name: airflow-webserver
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
    ports:
      - "8085:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: "airflow webserver"
    networks:
      - airflow-network
    depends_on:
      - postgres

  airflow-scheduler:
    image: apache/airflow:2.7.0-python3.9
    container_name: airflow-scheduler
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: "airflow scheduler"
    networks:
      - airflow-network
    depends_on:
      - postgres

  spark-master:
    image: bitnami/spark:3.4.0
    container_name: spark-master
    environment:
      - SPARK_MODE=master
    ports:
      - "8080:8080"
      - "7077:7077"
    networks:
      - spark-network

  spark-worker:
    image: bitnami/spark:3.4.0
    container_name: spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    depends_on:
      - spark-master
    networks:
      - spark-network

  metabase:
    image: metabase/metabase:v0.46.6
    container_name: metabase
    ports:
      - "3000:3000"
    volumes:
      - ./metabase_data:/metabase-data
    networks:
      - airflow-network

networks:
  airflow-network:
  spark-network:

volumes:
  db_data:
  metabase_data:

## 3. Configuración y Prueba de la Conexión entre Airflow y PostgreSQL
##    3.1. Configurar la Conexión en Airflow
        Acceder a la Interfaz Web de Airflow: Abre http://localhost:8085 en tu navegador.
        Configurar la Conexión postgres_default:
        Ir a "Admin" > "Connections".
        Crear una nueva conexión con los siguientes detalles:
        Conn Id: postgres_default
        Conn Type: Postgres
        Host: postgres (nombre del servicio definido en docker-compose.yml)
        Schema: tfb
        Login: edi
        Password: ${POSTGRES_PASSWORD}
        Port: 5432
        Extra: {}

##    3.2. Crear un DAG de Prueba
    Se creó un DAG de prueba llamado test_postgres_connection.py para verificar la conexión con PostgreSQL:
        from airflow import DAG
        from airflow.providers.postgres.operators.postgres import PostgresOperator
        from airflow.utils.dates import days_ago

        default_args = {
            'owner': 'airflow',
            'start_date': days_ago(1),
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1
        }

        with DAG(
            dag_id='test_postgres_connection',
            default_args=default_args,
            schedule_interval='@once',
        ) as dag:

            test_connection = PostgresOperator(
                task_id='test_postgres_query',
                postgres_conn_id='postgres_default',
                sql='SELECT 1;',
            )
##    3.3. Ejecutar el DAG de Prueba
        - Activar el DAG: Se activó el DAG test_postgres_connection desde la interfaz de Airflow.
        - Ejecutar el DAG: La ejecución se llevó a cabo correctamente, verificando que la conexión a PostgreSQL funciona.
    
## Conclusiones
    Hasta este punto, se ha configurado un entorno de trabajo con Airflow, PostgreSQL, Spark y Metabase, asegurando una conectividad adecuada entre Airflow y PostgreSQL para ejecutar tareas de ETL y análisis de datos. La conexión ha sido verificada mediante un DAG de prueba exitoso.
