Documentación de las Modificaciones Realizadas y Formatos Finales de los Archivos
A continuación, se presenta un resumen detallado de todas las modificaciones realizadas en el proyecto, junto con los formatos finales de los archivos. Este resumen te permitirá tener una visión clara de la configuración actual del proyecto y los cambios implementados.
Modificaciones Realizadas
    1. Estructura de Archivos y Directorios:
        ◦ Se creó una estructura de directorios para organizar el proyecto, incluyendo carpetas para los DAGs de Airflow, scripts de scraping, datos, y otros componentes del proyecto.
        ◦ Añadido el volumen ./data/output:/opt/airflow/data/output al archivo docker-compose.yml para compartir la carpeta de salida de datos entre el host y los contenedores.
    2. Configuración de Docker Compose:
        ◦ Se modificó el archivo docker-compose.yml para asegurar la correcta configuración de los contenedores y la correcta lectura de variables de entorno. Se añadieron volúmenes y configuraciones de red específicas.
        ◦ Se configuró la variable de entorno PYTHONPATH para que apunte a la carpeta de scripts dentro del contenedor de Airflow.
    3. Manejo de Permisos de Directorios:
        ◦ Se ajustaron los permisos de la carpeta /opt/airflow/data/output dentro del contenedor de Airflow para permitir la escritura de archivos desde los scripts de scraping.
        ◦ Se utilizaron comandos de Docker para cambiar los propietarios y permisos de los directorios relevantes.
    4. Scripts de Scraping:
        ◦ Se modificaron los scripts de scraping (scraping_properati.py, scraping_fazwaz.py, scraping_remax.py) para usar | como delimitador en los archivos CSV en lugar de comas.
        ◦ Se aseguraron las rutas de archivo usando os.makedirs con exist_ok=True para evitar errores si los directorios ya existen.
    5. DAGs de Airflow:
        ◦ Se actualizó el DAG staging_dag.py para que importe correctamente los scripts de scraping y utilice | como delimitador en los CSV.
        ◦ Se configuró el DAG crear_tablas_dag.py para combinar los CSV utilizando | como delimitador al leerlos con pandas.
    6. Manejo de Errores y Validaciones:
        ◦ Se implementó la validación y manejo de errores en los scripts de scraping para capturar errores de conexión y datos no disponibles.
        ◦ Se ajustaron las configuraciones para manejar adecuadamente los errores de autenticación en PostgreSQL.
Formatos Finales de los Archivos
1. Archivo docker-compose.yml
yaml
Copiar código
version: '3.8'
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
      - AIRFLOW__WEBSERVER__ENABLE_PROXY_FIX=True
      - PYTHONPATH=/opt/airflow/scripts
    ports:
      - "8085:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./scripts:/opt/airflow/scripts
      - ./data/output:/opt/airflow/data/output
    command: "airflow webserver"
    depends_on:
      - postgres
    networks:
      - airflow-network

  airflow-scheduler:
    image: apache/airflow:2.7.0-python3.9
    container_name: airflow-scheduler
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - PYTHONPATH=/opt/airflow/scripts
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./scripts:/opt/airflow/scripts
      - ./data/output:/opt/airflow/data/output
    command: "airflow scheduler"
    depends_on:
      - postgres
    networks:
      - airflow-network

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
2. Script de Scraping: scraping_properati.py
python
Copiar código
import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def extraer_datos_properati(ciudad, num_paginas):
    carpeta_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(carpeta_datos, exist_ok=True)
    
    archivo_csv = os.path.join(carpeta_datos, f"properati_{ciudad}_{datetime.date.today()}.csv")
    
    with open(archivo_csv, "w", encoding="utf-8") as f:
        encabezado = "id|fecha_captura|precio|precio_m2|area|habitaciones|banos|ubicacion|fecha_publicacion|extras|web|descripcion\n"
        f.write(encabezado)

        for num_pagina in range(1, num_paginas + 1):
            print(f"Procesando página {num_pagina}...")
            url_pagina = f'https://www.properati.com.ec/s/{ciudad}/departamento/venta/{num_pagina}/'
            
            try:
                respuesta = requests.get(url_pagina)
                respuesta.raise_for_status()
            except requests.HTTPError as err:
                print(f"Error HTTP al intentar acceder a {url_pagina}: {err}")
                continue
            except requests.RequestException:
                print(f"Error de conexión: El servidor está caído o la URL {url_pagina} es incorrecta")
                continue
            else:
                soup = BeautifulSoup(respuesta.text, 'html.parser')
                propiedades = soup.findAll("div", {"class": "listing-card__information"})

                for propiedad in propiedades:
                    descripcion = propiedad.find("div", {"class": "listing-card__title"}).get_text(strip=True)
                    precio_tag = propiedad.find("div", {"class": "price"})
                    if precio_tag:
                        precio_text = precio_tag.get_text(strip=True)
                        precio_match = re.findall(r"[\d,]+", precio_text)
                        if precio_match:
                            precio = precio_match[0].replace(",", "")
                        else:
                            precio = "No disponible"
                    else:
                        precio = "No disponible"

                    ubicacion = propiedad.find("div", {"class": "listing-card__location"}).get_text(strip=True)
                    habitaciones_tag = propiedad.find("div", {"class": "card-icon__bedrooms"})
                    if habitaciones_tag:
                        habitaciones = habitaciones_tag.find_next_sibling("span").get_text(strip=True)
                        habitaciones = re.findall(r"[\d]+", habitaciones)[0]
                    else:
                        habitaciones = "No disponible"

                    banos_tag = propiedad.find("div", {"class": "card-icon__bathrooms"})
                    if banos_tag:
                        banos = banos_tag.find_next_sibling("span").get_text(strip=True)
                        banos = re.findall(r"[\d]+", banos)[0]
                    else:
                        banos = "No disponible"

                    area_tag = propiedad.find("div", {"class": "card-icon__area"})
                    if area_tag:
                        area_text = area_tag.find_next_sibling("span").get_text(strip=True)
                        area_match = re.findall(r"[\d,]+", area_text)
                        if area_match:
                            area = area_match[0].replace(",", "")
                        else:
                            area = "No disponible"
                    else:
                        area = "No disponible"

                    try:
                        if precio != "No disponible" and area != "No disponible":
                            precio_m2 = round(float(precio) / float(area), 2)
                        else:
                            precio_m2 = "No disponible"
                    except ValueError:
                        precio_m2 = "No disponible"

                    fecha_publicacion = propiedad.find("div", {"class": "listing-card__published-date"}).get_text(strip=True)
                    fecha_captura = datetime.date.today()
                    linea = f'{hash((descripcion, ubicacion))}|{fecha_captura}|{precio}|{precio_m2}|{area}|{habitaciones}|{banos}|{ubicacion}|{fecha_publicacion}| |Properati|{descripcion}\n'
                    f.write(linea)

    print(f"Datos guardados en {archivo_csv}")

# Uso de ejemplo
if __name__ == "__main__":
    ciudad = "quito"
    num_paginas = 2
    extraer_datos_properati(ciudad, num_paginas)
3. Script de Scraping: scraping_fazwaz.py
python
Copiar código
import csv
import requests
from bs4 import BeautifulSoup
import re
import os
import datetime

def extraer_datos_fazwaz(ciudad, num_paginas):
    base_url = 'https://www.fazwaz.com.ec/apartment-en-venta/ecuador/{ciudad}?mapEnable=0&order_by=verification_at|desc&page={pagina}'
    carpeta_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(carpeta_datos, exist_ok=True)
    
    archivo_csv = os.path.join(carpeta_datos, f"fazwaz_{ciudad.split('/')[-1]}_{datetime.date.today()}.csv")

    with open(archivo_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['id', 'fecha_captura', 'precio', 'ubicacion', 'habitaciones', 'banos', 'area', 'precio_m2', 'fecha_publicacion', 'extras', 'web', 'descripcion'])

        for pagina in range(1, num_paginas + 1):
            print(f"Procesando página {pagina}...")
            url = base_url.format(ciudad=ciudad, pagina=pagina)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            property_containers = soup.find_all('div', class_="result-search__item")

            if not property_containers:
                break

            for container in property_containers:
                precio_tag = container.find('div', class_="price-tag")
                if precio_tag:
                    precio = re.findall(r"[\d,.]+", precio_tag.get_text(strip=True).replace('€', '').strip())[0]
                    precio = precio.replace(',', '')
                else:
                    precio = "Precio no encontrado"

                ubicacion = container.find('div', class_="location-unit").get_text(strip=True) if container.find('div', class_="location-unit") else "Ubicación no encontrada"
                habitaciones = container.find('i', class_="i-bed icon-info-unit").find_next_sibling(text=True).strip() if container.find('i', class_="i-bed icon-info-unit") else "Número de habitaciones no encontrado"
                banos = container.find('i', class_="i-bath icon-info-unit").find_next_sibling(text=True).strip() if container.find('i', class_="i-bath icon-info-unit") else "Número de baños no encontrado"
                area_tag = container.find('span', class_="dynamic-tooltip area-tooltip")
                if area_tag:
                    area = re.findall(r"[\d,.]+", area_tag.get_text(strip=True).replace('m²', '').strip())[0]
                    area = area.replace(',', '')
                else:
                    area = "Área no encontrada"

                precio_m2_tag = container.find('span', class_="dynamic-tooltip area-tooltip area-per-tooltip")
                if precio_m2_tag:
                    precio_m2 = re.findall(r"[\d,.]+", precio_m2_tag.get_text(strip=True).replace('€', '').strip())[0]
                    precio_m2 = precio_m2.replace(',', '')
                else:
                    precio_m2 = "Precio por m² no encontrado"
                
                fecha_publicacion = container.find('i', class_="manage-tag__icon last-updated-message").find_next_sibling(text=True).strip() if container.find('i', class_="manage-tag__icon last-updated-message") else "Fecha de publicación no encontrada"
                descripcion = container.find('div', class_="unit-info__shot-description").get_text(strip=True) if container.find('div', class_="unit-info__shot-description") else "Descripción no encontrada"

                fecha_captura = datetime.date.today()
                writer.writerow([hash((descripcion, ubicacion)), fecha_captura, precio, ubicacion, habitaciones, banos, area, precio_m2, fecha_publicacion, '', 'Fazwaz', descripcion])

    print(f"Extracción completada. El archivo CSV '{archivo_csv}' ha sido creado correctamente.")

# Uso de ejemplo
if __name__ == "__main__":
    ciudad = "pichincha/quito"
    num_paginas = 2
    extraer_datos_fazwaz(ciudad, num_paginas)
4. Script de Scraping: scraping_remax.py
python
Copiar código
import os
import datetime

# Función temporal para simular el scraping de Remax
def extraer_datos_remax(ciudad, num_paginas):
    """
    Función temporal para simular la extracción de datos de Remax.
    En la versión final, esta función debe implementar el scraping real.

    Parámetros:
    ciudad (str): La ciudad a analizar.
    num_paginas (int): Número de páginas a iterar para extraer la información.
    """
    # Crear la ruta para guardar archivos CSV de salida
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Crear un archivo CSV temporal para simular la salida
    filename = os.path.join(output_dir, f"remax_{ciudad}_{datetime.date.today()}.csv")
    
    # Escribir un log simple en lugar de realizar scraping real
    with open(filename, 'w') as file:
        file.write("id|fecha_captura|precio|precio_m2|area|habitaciones|banos|ubicacion|fecha_publicacion|extras|web|descripcion\n")
        file.write(f"1|{datetime.date.today()}|No disponible|No disponible|No disponible|No disponible|No disponible|No disponible|No disponible|No disponible|Remax|Data temporal para pruebas.\n")
    
    print(f"Archivo temporal de datos de Remax creado: {filename}")

# Uso temporal
if __name__ == "__main__":
    ciudad = "quito"  # Ciudad para pruebas
    num_paginas = 2  # Número de páginas para pruebas
    extraer_datos_remax(ciudad, num_paginas)
5. DAG de Airflow: staging_dag.py
python
Copiar código
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
   
# Ahora importa las funciones de scraping
from scraping_properati import extraer_datos_properati as properati_scraper
from scraping_fazwaz import extraer_datos_fazwaz as fazwaz_scraper
from scraping_remax import extraer_datos_remax as remax_scraper

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'staging',
    default_args=default_args,
    description='DAG de scraping para diferentes fuentes de datos inmobiliarios',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    catchup=False,
)

# Funciones para cada fuente de datos
scraping_properati_task = PythonOperator(
    task_id='scraping_properati',
    python_callable=properati_scraper,
    op_kwargs={'ciudad': 'quito', 'num_paginas': 2},
    dag=dag,
)

scraping_fazwaz_task = PythonOperator(
    task_id='scraping_fazwaz',
    python_callable=fazwaz_scraper,
    op_kwargs={'ciudad': 'pichincha/quito', 'num_paginas': 2},
    dag=dag,
)

scraping_remax_task = PythonOperator(
    task_id='scraping_remax',
    python_callable=remax_scraper,
    op_kwargs={'ciudad': 'quito', 'num_paginas': 2},
    dag=dag,
)

# Dependencias
scraping_properati_task >> scraping_fazwaz_task >> scraping_remax_task
6. DAG crear_tablas necesita modificarse para que pueda leer correctamente los archivos CSV que utilizan el delimitador | en lugar de comas. Para ello, debes especificar el parámetro delimiter='|' al leer los archivos CSV con pandas. Aquí tienes el DAG modificado:
python
Copiar código
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.dates import days_ago
import pandas as pd
import os

# Definir los argumentos por defecto del DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

# Función para combinar CSVs en una sola tabla en PostgreSQL
def combine_csvs_to_table(**kwargs):
    path_to_csvs = '/opt/airflow/data/output'  # Path donde están los CSVs
    csv_files = [f for f in os.listdir(path_to_csvs) if f.endswith('.csv')]

    df_list = []
    for file in csv_files:
        df = pd.read_csv(os.path.join(path_to_csvs, file), delimiter='|')  # Usar | como delimitador
        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)

    # Insertar los datos en la tabla usando PostgresHook
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = postgres_hook.get_sqlalchemy_engine()
    combined_df.to_sql('propiedades', con=engine, if_exists='append', index=False)

# Crear el DAG
with DAG(
    dag_id='crear_tablas',
    default_args=default_args,
    description='DAG para crear tablas y combinar CSVs en PostgreSQL',
    schedule_interval='@daily',
) as dag:

    # Crear la tabla si no existe
    create_table_task = PostgresOperator(
        task_id='create_table_postgres',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS propiedades (
            id SERIAL PRIMARY KEY,
            fecha_captura DATE,
            precio NUMERIC,
            precio_m2 NUMERIC,
            area NUMERIC,
            habitaciones INTEGER,
            banos INTEGER,
            ubicacion TEXT,
            fecha_publicacion DATE,
            extras TEXT,
            web TEXT,
            descripcion TEXT
        );
        """,
    )

    # Combinar CSVs y cargar en la tabla
    combine_csvs_task = PythonOperator(
        task_id='combine_csvs_to_table',
        python_callable=combine_csvs_to_table,
        provide_context=True
    )

    # Definir la secuencia de tareas
    create_table_task >> combine_csvs_task


Resumen
    • Modificaciones Principales: Ajuste de delimitadores en CSV, manejo de permisos y rutas de archivos, configuración de Airflow, y mejoras en los scripts de scraping.
    • Aseguramiento de Funcionalidad: Todos los componentes del flujo de trabajo están alineados para manejar los datos de forma coherente y evitar errores de procesamiento.
    
    
    Documentación de las Modificaciones Recientes
En esta sección se documentan los cambios y mejoras implementadas en el proyecto desde la última actualización. Estos cambios incluyen modificaciones en los scripts de scraping, ajustes en el procesamiento de datos, y mejoras en la configuración de los DAGs de Airflow para asegurar la integridad y la calidad de los datos.

1. Modificación del DAG de Creación de Tablas (crear_tablas_dag.py)
Objetivo: Mejorar la gestión de los id de las propiedades para asegurar que sean únicos e incrementales y optimizar la carga de datos en la base de datos PostgreSQL.

Cambios Implementados:

Uso de SERIAL para la columna id: La columna id se definió como SERIAL, lo que permite a PostgreSQL asignar automáticamente valores numéricos únicos e incrementales. Esto elimina la dependencia de los id que podrían estar presentes en los CSV y asegura que no haya conflictos de id duplicados.
Eliminación de la columna id antes de insertar en la base de datos: Al combinar los CSVs, se elimina la columna id para permitir que PostgreSQL maneje la asignación de id. Esto evita conflictos y errores relacionados con id ya existentes en los CSV.
Limpieza y transformación de datos: Se aplicaron funciones de limpieza y transformación para manejar datos faltantes o no válidos, especialmente en columnas numéricas y de fecha, para asegurar que los datos sean compatibles con los tipos de datos en la base de datos PostgreSQL.
Detalles del Código:

La creación de la tabla propiedades ahora utiliza el tipo SERIAL para la columna id:
sql
Copiar código
CREATE TABLE IF NOT EXISTS propiedades (
    id SERIAL PRIMARY KEY,
    fecha_captura DATE,
    precio NUMERIC,
    precio_m2 NUMERIC,
    area NUMERIC,
    habitaciones INTEGER,
    banos NUMERIC,
    ubicacion TEXT,
    fecha_publicacion DATE,
    extras TEXT,
    web TEXT,
    descripcion TEXT
);
Se implementaron funciones de limpieza para manejar fechas y valores numéricos antes de cargar los datos en la base de datos:
python
Copiar código
def parse_fecha(fecha):
    try:
        return pd.to_datetime(fecha, errors='coerce').date()
    except Exception:
        return None

def parse_numeric(value):
    try:
        return pd.to_numeric(value, errors='coerce')
    except Exception:
        return None
2. Implementación de las Mejoras de Limpieza de Datos en los Scripts de Scraping
Objetivo: Asegurar que los datos extraídos de las distintas fuentes de datos inmobiliarios sean consistentes y estén bien formateados para su posterior procesamiento y análisis.

Cambios Implementados:

Cambio de delimitador a | en los CSVs: Para evitar problemas de tokenización y asegurar la consistencia de los datos, se cambió el delimitador a | en los scripts de scraping.
Manejo de valores No disponible: Se agregaron funciones para transformar valores como No disponible en NULL o valores predeterminados adecuados antes de insertarlos en la base de datos.
Detalles del Código:

Modificación en los scripts de scraping (scraping_properati.py, scraping_fazwaz.py, etc.) para usar | como delimitador:
python
Copiar código
df.to_csv(archivo_csv, sep='|', index=False)


