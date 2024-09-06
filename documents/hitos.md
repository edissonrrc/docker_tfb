## ﻿Hitos del Proyecto
	    1. Preparación del Entorno
		◦ Actualizar los repositorios de apt
		◦ Instalar Docker y Docker Compose
		◦ Configurar permisos para Docker
	    2. Configuración Inicial del Proyecto
		◦ Crear directorio del proyecto proyecto_tfb
		◦ Definir la estructura básica de directorios (dags, logs, plugins, db_data, etc.)
	    3. Crear y Configurar el Archivo .env
		◦ Crear el archivo .env con las credenciales de PostgreSQL y Airflow
	    4. Configuración Inicial de Docker Compose
		◦ Crear un archivo docker-compose.yml simplificado para Airflow y PostgreSQL
		◦ Probar la configuración inicial levantando los servicios
	    5. Configuración Completa de Docker Compose
		◦ Ampliar el archivo docker-compose.yml para incluir Spark y Metabase
		◦ Definir redes y volúmenes en Docker Compose
		◦ Probar la configuración completa levantando todos los servicios
	    6. Crear Entorno Virtual de Python
		◦ Crear y activar un entorno virtual
		◦ Crear un archivo requirements.txt inicial
		◦ Instalar las dependencias desde requirements.txt
		◦ Congelar las dependencias en requirements.txt
	    7. Configuración de Airflow
		◦ Acceder a la interfaz web de Airflow
		◦ Configurar la conexión postgres_default en Airflow
		◦ Crear un DAG de prueba para verificar la conexión con PostgreSQL
		◦ Ejecutar y verificar el éxito del DAG de prueba
	    8. Desarrollo de DAGs de Producción
		◦ Crear DAGs para tareas específicas (scraping, transformación, carga en PostgreSQL)
		◦ Implementar lógica de ETL en los DAGs
		◦ Probar y validar los DAGs de producción
	    9. Configuración de Metabase
		◦ Acceder a la interfaz web de Metabase
		◦ Conectar Metabase a la base de datos PostgreSQL
		◦ Crear visualizaciones básicas para explorar los datos
	    10. Documentación y Registro del Proyecto
		◦ Documentar los pasos de configuración y desarrollo
		◦ Subir archivos y documentación al repositorio de GitHub

## Duración Estimada y Dependencias entre Hitos
    • Preparación del Entorno: 1 día
        ◦ Dependencia: Ninguna
    • Configuración Inicial del Proyecto: 1 día
        ◦ Dependencia: Preparación del Entorno
    • Crear y Configurar el Archivo .env: 0.5 días
        ◦ Dependencia: Configuración Inicial del Proyecto
    • Configuración Inicial de Docker Compose: 1 día
        ◦ Dependencia: Crear y Configurar el Archivo .env
    • Configuración Completa de Docker Compose: 2 días
        ◦ Dependencia: Configuración Inicial de Docker Compose
    • Crear Entorno Virtual de Python: 0.5 días
        ◦ Dependencia: Configuración Inicial del Proyecto
    • Configuración de Airflow: 1 día
        ◦ Dependencia: Configuración Completa de Docker Compose, Crear Entorno Virtual de Python
    • Desarrollo de DAGs de Producción: 5 días
        ◦ Dependencia: Configuración de Airflow
    • Configuración de Metabase: 1 día
        ◦ Dependencia: Configuración Completa de Docker Compose
    • Documentación y Registro del Proyecto: 1 día
        ◦ Dependencia: Desarrollo de DAGs de Producción, Configuración de Metabase

## Visualización en Gráfica Gantt
Cada hito puede representarse como una barra en la gráfica, con flechas que indican las dependencias entre los hitos. A continuación, se presenta una forma simplificada de cómo se pueden organizar los hitos en la gráfica Gantt:

    1. Día 1: Preparación del Entorno
    2. Día 2: Configuración Inicial del Proyecto
    3. Día 3: Crear y Configurar el Archivo .env
    4. Día 3-4: Configuración Inicial de Docker Compose
    5. Día 5-6: Configuración Completa de Docker Compose
    6. Día 3: Crear Entorno Virtual de Python
    7. Día 7: Configuración de Airflow
    8. Día 8-12: Desarrollo de DAGs de Producción
    9. Día 7-8: Configuración de Metabase
    10. Día 13: Documentación y Registro del Proyecto
    
Con esta lista de hitos y la duración estimada, podrás organizar y planificar eficazmente las tareas para el desarrollo de tu proyecto, asegurando que cada fase se complete en el tiempo previsto y que todas las dependencias se gestionen adecuadamente.

## Hitos Adicionales del Proyecto
	Hito 11: Desarrollo y Configuración de Scripts de Scraping
	    • Descripción: Implementar y optimizar los scripts de scraping para diferentes plataformas inmobiliarias.
	    • Tareas:
		◦ Desarrollar y probar el script de scraping para Properati (scraping_properati.py).
		◦ Desarrollar y probar el script de scraping para Fazwaz (scraping_fazwaz.py).
		◦ Implementar un script temporal para Remax para asegurar la integración inicial.
	    • Dependencia: Desarrollo de DAGs de Producción
	    • Duración Estimada: 3 días
	Hito 12: Implementación de DAGs para Orquestación de Scraping
	    • Descripción: Configurar y desplegar los DAGs en Airflow para la ejecución de los scripts de scraping y consolidación de datos.
	    • Tareas:
		◦ Crear y configurar el staging_dag.py para orquestar los scripts de scraping.
		◦ Crear y configurar el crear_tablas_dag.py para la creación de tablas en PostgreSQL y la combinación de archivos CSV.
		◦ Probar los DAGs y validar que se ejecuten correctamente y sin errores.
	    • Dependencia: Configuración de Airflow, Desarrollo y Configuración de Scripts de Scraping
	    • Duración Estimada: 2 días
	Hito 13: Generación de Diagramas de Gantt
	    • Descripción: Implementar un script para generar diagramas de Gantt que visualicen el progreso del proyecto.
	    • Tareas:
		◦ Desarrollar el script generador_gantt.py utilizando matplotlib para visualizar las fases y los hitos del proyecto.
		◦ Configurar el script para guardar los gráficos en la carpeta images/.
		◦ Ejecutar y validar el diagrama de Gantt generado para asegurar que refleje el estado actual del proyecto.
	    • Dependencia: Documentación y Registro del Proyecto
	    • Duración Estimada: 1 día
	Hito 14: Ajustes Finaels y Validación de la Integración Completa
	    • Descripción: Realizar ajustes finales y validar que todos los componentes del proyecto funcionen de manera integrada.
	    • Tareas:
		◦ Validar la ejecución de los DAGs en Airflow con todos los scripts de scraping integrados.
		◦ Asegurarse de que los datos se están almacenando correctamente en PostgreSQL.
		◦ Revisar la documentación para asegurar que esté actualizada y sea precisa.
	    • Dependencia: Implementación de DAGs para Orquestación de Scraping, Generación de Diagramas de Gantt
	    • Duración Estimada: 2 días
	Hito 15: Documentación Completa del Proyecto
	    • Descripción: Compilar y organizar toda la documentación del proyecto, asegurando que todos los componentes estén cubiertos.
	    • Tareas:
		◦ Documentar el funcionamiento de los scripts de scraping y cómo integrarlos con Airflow.
		◦ Detallar el uso de los DAGs de Airflow para la orquestación de tareas.
		◦ Incluir la documentación de cómo se generan y utilizan los diagramas de Gantt para el seguimiento del proyecto.
		◦ Actualizar el archivo requirements.txt y documentar las dependencias.
		◦ Revisar y actualizar el archivo .gitignore según los archivos generados y las nuevas configuraciones.
	    • Dependencia: Ajustes Finales y Validación de la Integración Completa
	    • Duración Estimada: 1 día
	Duración Estimada y Dependencias entre Hitos (Actualizado)
	    • Desarrollo y Configuración de Scripts de Scraping: 3 días
		◦ Dependencia: Desarrollo de DAGs de Producción
	    • Implementación de DAGs para Orquestación de Scraping: 2 días
		◦ Dependencia: Configuración de Airflow, Desarrollo y Configuración de Scripts de Scraping
	    • Generación de Diagramas de Gantt: 1 día
		◦ Dependencia: Documentación y Registro del Proyecto
	    • Ajustes Finales y Validación de la Integración Completa: 2 días
		◦ Dependencia: Implementación de DAGs para Orquestación de Scraping, Generación de Diagramas de Gantt
	    • Documentación Completa del Proyecto: 1 día
		◦ Dependencia: Ajustes Finales y Validación de la Integración Completa

## Visualización en Gráfica Gantt (Actualizado)
Con los hitos adicionales, la gráfica Gantt se puede actualizar para incluir las nuevas tareas y dependencias. Los hitos se representan como barras con flechas que indican las dependencias.

    • Día 14-16: Desarrollo y Configuración de Scripts de Scraping
    • Día 17-18: Implementación de DAGs para Orquestación de Scraping
    • Día 19: Generación de Diagramas de Gantt
    • Día 20-21: Ajustes Finales y Validación de la Integración Completa
    • Día 22: Documentación Completa del Proyecto

Estos hitos adicionales reflejan el progreso reciente del proyecto y proporcionan una guía clara para completar el trabajo restante. Esta planificación asegura que el proyecto avance de manera ordenada y eficiente, con un enfoque en la integración y documentación completa de todos los componentes.

