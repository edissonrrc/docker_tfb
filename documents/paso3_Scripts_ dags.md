## Documentación de la fase 3, scripts, dags, csv, requirements y entorno actualizado.
En esta sección, se detallarán los cambios y actualizaciones realizados recientemente en el proyecto de scraping y análisis de datos inmobiliarios. Esto incluye la estructura del proyecto, los scripts de scraping, los DAGs de Airflow y otras configuraciones esenciales.

## 1. Estructura de Directorios del Proyecto
La organización de los directorios del proyecto se ha definido para facilitar la gestión y el mantenimiento del código, datos y scripts. La estructura es la siguiente:
proyecto_tfb/
├── dags/                     # Almacena los DAGs de Airflow
│   ├── staging_dag.py
│   └── crear_tablas_dag.py
├── logs/                     # Almacena los logs generados por Airflow
├── plugins/                  # Almacena los plugins de Airflow
├── scripts/                  # Almacena los scripts de scraping
│   ├── scraping_properati.py
│   ├── scraping_fazwaz.py
│   └── scraping_remax.py
├── data/
│   ├── csv/                  # Archivos CSV de entrada
│   ├── output/               # Salida de datos procesados (CSV generados)
│   └── html/                 # HTML descargado para posterior captura de datos
├── db_data/                  # Directorio de datos persistentes para PostgreSQL
├── metabase_data/            # Directorio de datos para Metabase
├── images/                   # Carpeta para almacenar gráficos generados (e.g., diagramas de Gantt)
├── .env                      # Archivo de variables de entorno
├── .gitignore                # Archivo para ignorar archivos específicos en Git
├── docker-compose.yml        # Archivo de configuración de Docker Compose
├── Dockerfile                # Archivo de configuración de la imagen de Docker
└── requirements.txt          # Archivo de dependencias del proyecto

## 2. Configuración del Archivo .env
El archivo .env contiene variables de entorno sensibles, como credenciales de la base de datos y configuraciones de usuario. Este archivo debe mantenerse seguro y no subirse a Git.

## 3. Actualización del Archivo docker-compose.yml
El archivo docker-compose.yml ha sido actualizado para reflejar la configuración de contenedores de Docker necesarios para el proyecto. Esta configuración permite levantar instancias de PostgreSQL, Airflow, Spark y Metabase.

## 4. Scripts de Scraping
Se han desarrollado y modificado scripts de scraping para Properati y Fazwaz, además de un script temporal para Remax.

scraping_properati.py
Ubicado en: proyecto_tfb/scripts/scraping_properati.py
Este script extrae datos de propiedades desde Properati y guarda los resultados en un archivo CSV.

	import os
	import requests
	from bs4 import BeautifulSoup
	import re
	import datetime

	def extraer_datos_propiedades(ciudad, num_paginas):
	    carpeta_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
	    if not os.path.exists(carpeta_datos):
		os.makedirs(carpeta_datos)
	    
	    archivo_csv = os.path.join(carpeta_datos, f"properati_{ciudad}_{datetime.date.today()}.csv")
	    
	    with open(archivo_csv, "w", encoding="utf-8") as f:
		encabezado = "id,fecha_captura,precio,precio_m2,area,habitaciones,banos,ubicacion,fecha_publicacion,extras,web,descripcion\n"
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

		            linea = f'{id(fecha_captura)},{fecha_captura},{precio},{precio_m2},{area},{habitaciones},{banos},{ubicacion},{fecha_publicacion},,{descripcion}\n'
		            
		            f.write(linea)

	    print(f"Datos guardados en {archivo_csv}")

	# Uso de ejemplo
	if __name__ == "__main__":
	    ciudad = "quito"
	    num_paginas = 2
	    extraer_datos_propiedades(ciudad, num_paginas)


scraping_fazwaz.py
Ubicado en: proyecto_tfb/scripts/scraping_fazwaz.py
Este script extrae datos de propiedades desde Fazwaz y guarda los resultados en un archivo CSV.

	import csv
	import requests
	from bs4 import BeautifulSoup
	import re
	import os
	import datetime

	def extraer_datos_propiedades(ciudad, num_paginas):
	    base_url = 'https://www.fazwaz.com.ec/apartment-en-venta/ecuador/{ciudad}?mapEnable=0&order_by=verification_at|desc&page={pagina}'
	    carpeta_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
	    if not os.path.exists(carpeta_datos):
		os.makedirs(carpeta_datos)
	    
	    archivo_csv = os.path.join(carpeta_datos, f"fazwaz_{ciudad.split('/')[-1]}_{datetime.date.today()}.csv")

	    with open(archivo_csv, 'w', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
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

		        writer.writerow([id(fecha_captura), fecha_captura, precio, ubicacion, habitaciones, banos, area, precio_m2, fecha_publicacion, '', 'Fazwaz', descripcion])

	    print(f"Extracción completada. El archivo CSV '{archivo_csv}' ha sido creado correctamente.")

	# Uso de ejemplo
	if __name__ == "__main__":
	    ciudad = "pichincha/quito"
	    num_paginas = 20
	    extraer_datos_propiedades(ciudad, num_paginas)


scraping_remax.py (Temporal)
Ubicado en: proyecto_tfb/scripts/scraping_remax.py
Este script es temporal y está configurado para pruebas de integración.

## 5. DAGs en Airflow
staging_dag.py
Ubicado en: proyecto_tfb/dags/staging_dag.py
Este DAG orquesta la ejecución de los scripts de scraping para diferentes plataformas inmobiliarias.
Tareas incluidas:
scraping_properati: Llama al script de Properati para realizar scraping.
scraping_fazwaz: Llama al script de Fazwaz para realizar scraping.
scraping_remax: Llama al script temporal de Remax para realizar pruebas.

	from airflow import DAG
	from airflow.operators.python import PythonOperator
	from airflow.utils.dates import days_ago
	from datetime import timedelta

	# Importamos las funciones de scraping desde los scripts
	from scripts.scraping_properati import extraer_datos_propiedades as properati_scraper
	from scripts.scraping_fazwaz import extraer_datos_fazwaz as fazwaz_scraper
	from scripts.scraping_remax import extraer_datos_remax as remax_scraper

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
	[scraping_properati_task, scraping_fazwaz_task, scraping_remax_task]


crear_tablas_dag.py
Ubicado en: proyecto_tfb/dags/crear_tablas_dag.py
Este DAG es responsable de crear la tabla propiedades en PostgreSQL, si no existe, y luego consolidar los datos de los CSV generados por los scrapers.

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
	    path_to_csvs = '/home/edisson/Descargas/proyecto_tfb/data/csv'  # Path donde están los CSVs
	    csv_files = [f for f in os.listdir(path_to_csvs) if f.endswith('.csv')]

	    df_list = []
	    for file in csv_files:
		df = pd.read_csv(os.path.join(path_to_csvs, file))
		df_list.append(df)

	    combined_df = pd.concat(df_list, ignore_index=True)

	    # Insertar los datos en la tabla usando PostgresHook
	    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
	    engine = postgres_hook.get_sqlalchemy_engine()
	    combined_df.to_sql('propiedades', con=engine, if_exists='append', index=False)

	# Crear el DAG
	with DAG(
	    dag_id='postgres_etl_dag',
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


## 6. Generador de Diagramas de Gantt
Se ha desarrollado un script para generar un diagrama de Gantt que visualiza las fases y hitos del proyecto.
Ubicado en: proyecto_tfb/scripts/generador_gantt.py
Características del Script:
Genera un gráfico Gantt utilizando matplotlib.
Los resultados se guardan en la carpeta images/ con el nombre gantt_tfb.png.

	import matplotlib.pyplot as plt
	import pandas as pd
	import matplotlib.dates as mdates
	from matplotlib.dates import DateFormatter
	import os

	# Ruta absoluta o relativa desde la raíz del proyecto para la carpeta "images"
	root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Subir un nivel desde scripts
	images_dir = os.path.join(root_dir, 'images')

	# Crear la carpeta "images" si no existe
	if not os.path.exists(images_dir):
	    os.makedirs(images_dir)

	# Datos del proyecto con fases y hitos
	data = {
	    'Tarea': [
		'Fase 1: Configuración y Preparación de Datos', 
		'Hito 1: Entorno configurado', 
		'Hito 2: Datos recolectados y limpios', 
		'Hito 3: Base de datos operativa',
		'Fase 2: Análisis Exploratorio de Datos', 
		'Hito 4: Análisis descriptivo completo', 
		'Hito 5: Mapas preliminares generados', 
		'Hito 6: Correlaciones y patrones identificados',
		'Fase 3: Desarrollo del Modelo Predictivo', 
		'Hito 7: Modelos implementados', 
		'Hito 8: Optimización de modelos', 
		'Hito 9: Selección del modelo final',
		'Fase Final: Presentación de Resultados y Documentación Final', 
		'Hito 10: API desarrollada y probada', 
		'Hito 11: Interfaz web completa', 
		'Hito 12: Proyecto desplegado',
		'Hito 13: Documentación final preparada',
		'Depósito TFB'
	    ],
	    'Inicio': [
		'2024-07-16', '2024-07-16', '2024-07-18', '2024-07-20', 
		'2024-07-23', '2024-07-23', '2024-07-28', '2024-08-05', 
		'2024-08-12', '2024-08-12', '2024-08-18', '2024-08-25', 
		'2024-09-02', '2024-09-02', '2024-09-08', '2024-09-13', 
		'2024-09-14', '2024-09-16'
	    ],
	    'Fin': [
		'2024-07-22', '2024-07-18', '2024-07-20', '2024-07-22', 
		'2024-08-11', '2024-07-27', '2024-08-04', '2024-08-10', 
		'2024-09-01', '2024-08-17', '2024-08-24', '2024-08-31', 
		'2024-09-15', '2024-09-07', '2024-09-12', '2024-09-13', 
		'2024-09-15', '2024-09-23'
	    ]
	}

	# Crear DataFrame
	df = pd.DataFrame(data)

	# Convertir las fechas a datetime
	df['Inicio'] = pd.to_datetime(df['Inicio'])
	df['Fin'] = pd.to_datetime(df['Fin'])

	# Crear el gráfico Gantt
	fig, ax = plt.subplots(figsize=(14, 10))

	# Colores para los meses
	colors = ['#FFDDC1', '#FFABAB', '#FFC3A0']

	# Rellenar el fondo de los meses
	start_month = pd.Timestamp('2024-07-16')
	end_month = pd.Timestamp('2024-09-23')

	for i, month_start in enumerate(pd.date_range(start=start_month, end=end_month, freq='MS')):
	    month_end = (month_start + pd.offsets.MonthEnd(1)).replace(hour=23, minute=59, second=59)
	    ax.axvspan(month_start, month_end, facecolor=colors[i % len(colors)], alpha=0.2)
	    ax.axvline(x=month_start, color='black', linestyle='--', linewidth=1)

	# Añadir las barras del Gantt
	for i, (tarea, inicio, fin) in enumerate(zip(df['Tarea'], df['Inicio'], df['Fin'])):
	    if tarea == 'Depósito TFB':
		color = 'darkblue'
		height = 0.6
	    elif 'Fase' in tarea:
		color = 'lightgreen'
		height = 0.3
	    else:
		color = 'lightskyblue'
		height = 0.3
	    ax.barh(tarea, (fin - inicio).days, left=inicio, color=color, height=height)

	# Formatear fechas en el eje x
	ax.set_xlim([start_month, end_month])
	ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
	ax.xaxis.set_major_formatter(DateFormatter("%d"))

	# Añadir cuadrícula
	ax.grid(True, which='major', axis='x', color='gray', linestyle='--', linewidth=0.5)

	# Añadir segunda fila para los meses
	ax_secondary = ax.twiny()
	ax_secondary.set_xlim(ax.get_xlim())
	ax_secondary.xaxis.set_major_locator(mdates.MonthLocator())
	ax_secondary.xaxis.set_major_formatter(DateFormatter("%B"))
	ax_secondary.tick_params(axis='x', which='major', pad=20, labelsize=12)

	# Añadir etiquetas y título
	ax.set_xlabel('Días del Mes', fontsize=12, fontweight='bold')
	ax.set_title('Diagrama de Gantt del Proyecto: Modelado Predictivo de la Asequibilidad de Vivienda en Quito', fontsize=14, fontweight='bold', color='darkblue')

	# Mejorar presentación
	ax.set_facecolor('#f9f9f9')
	ax.invert_yaxis()

	# Ajustar orden de las fases y hitos para que aparezcan de arriba hacia abajo
	for label in ax.get_yticklabels():
	    tarea_text = label.get_text()
	    if 'Fase' in tarea_text or 'Depósito TFB' in tarea_text:
		label.set_fontweight('bold')
	    label.set_horizontalalignment('right')
	    label.set_x(-0.05)

	# Añadir una marca de agua en la esquina inferior derecha
	fig.text(0.95, 0.01, 'Edisson Reyes', fontsize=12, color='gray', ha='right', va='bottom', alpha=0.5)

	# Guardar la imagen en la carpeta "images"
	gantt_image_path = os.path.join(images_dir, 'gantt_tfb.png')
	plt.savefig(gantt_image_path, dpi=300, bbox_inches='tight')

	# Mostrar el gráfico
	plt.show()


## 7. Actualización del Archivo requirements.txt
Se ha actualizado el archivo requirements.txt para incluir todas las dependencias necesarias para los scripts de scraping, generación de gráficos y ejecución de DAGs en Airflow.
	Contenido actualizado del requirements.txt:
	apache-airflow==2.7.0
	psycopg2-binary==2.9.1
	pandas==1.3.3
	requests==2.26.0
	beautifulsoup4==4.10.0
	matplotlib==3.4.3

## 8. Configuración del Archivo .gitignore
El archivo .gitignore ha sido configurado para evitar que ciertos archivos y directorios sensibles o generados automáticamente sean incluidos en el repositorio Git.
	Contenido del .gitignore:
	# Archivos de entorno virtual
	venv/
	*.pyc

	# Archivos de configuración locales
	.env

	# Archivos de datos
	db_data/
	metabase_data/
	data/csv/
	data/output/
	data/html/

	# Archivos generados
	logs/
	*.log
	images/

	# Configuración de IDEs
	.idea/
	.vscode/

## Resumen y Siguientes Pasos
En resumen, hemos establecido una estructura de proyecto profesional, implementado y configurado scripts de scraping y DAGs de Airflow, y creado herramientas para la visualización de progreso. Los próximos pasos incluirán:
1. Desarrollo completo de los scripts de scraping faltantes.
2. Integración de los DAGs de Airflow con los scripts de scraping completos.
3. Realización de pruebas de los scripts y DAGs en un entorno de desarrollo.
4. Documentación adicional y optimización del código según sea necesario.

Esta documentación proporciona una guía completa sobre las configuraciones y desarrollos recientes, asegurando que el proyecto sea gestionable, escalable y esté alineado con las mejores prácticas de la industria.
