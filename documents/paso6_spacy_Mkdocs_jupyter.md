Documentación de Seguimiento: Configuración del Entorno Docker para NLP
1. Inicio del Proyecto
Fecha: [Fecha de inicio]
Objetivo Inicial: Configurar un entorno de contenedores Docker usando Docker Compose para orquestar diferentes servicios necesarios para un proyecto de procesamiento de lenguaje natural (NLP), incluyendo Apache Airflow, Spark, Metabase, Jupyter, MkDocs y Postgres.
2. Creación del Directorio del Proyecto
Acción: Crear un directorio principal para el proyecto.
Comando:
bash
Copiar código
mkdir mi_proyecto_docker
cd mi_proyecto_docker
Observación: Se definió mi_proyecto_docker como el directorio raíz para todos los archivos relacionados con el proyecto.
3. Configuración Inicial del Archivo docker-compose.yml
Acción: Crear un archivo docker-compose.yml para definir los servicios.
Contenido Inicial: Incluía servicios para Airflow, Spark (Master y Worker), Postgres, Metabase, Jupyter, y MkDocs.
Problema Encontrado: Incompatibilidad entre Airflow y Spark, dificultades de integración y complejidad innecesaria para el volumen de datos manejado.
4. Decisión de Eliminar Spark
Fecha: [Fecha de decisión]
Razón: Problemas de compatibilidad con Airflow y simplificación del entorno debido a un volumen de datos manejable que no requiere procesamiento distribuido.
Acción: Eliminar las definiciones de spark-master y spark-worker del archivo docker-compose.yml.
5. Integración de spaCy para NLP
Fecha: [Fecha de integración]
Acción: Decisión de utilizar spaCy como la principal herramienta para tareas de NLP.
Pasos Tomados:
Crear un archivo requirements.txt con el contenido:
text
Copiar código
spacy
Crear un Dockerfile para Airflow:
Dockerfile
Copiar código
FROM apache/airflow:2.10.0
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
Actualizar docker-compose.yml para usar el Dockerfile personalizado:
yaml
Copiar código
airflow:
  build:
    context: .
    dockerfile: Dockerfile
  environment:
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://user:password@postgres/mydb
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
  networks:
    - mynetwork
  depends_on:
    - postgres
  entrypoint: >
    bash -c "airflow db upgrade &&
             airflow users create --username admin --password admin --firstname Admin --lastname Admin --role Admin --email admin@example.com &&
             airflow webserver"
  ports:
    - "8080:8080"
6. Configuración y Ejecución de MkDocs
Fecha: [Fecha de configuración]
Acción: Implementar MkDocs para manejar la documentación del proyecto.
Pasos Tomados:
Añadir servicio de MkDocs a docker-compose.yml:
yaml
Copiar código
mkdocs:
  image: squidfunk/mkdocs-material:latest
  ports:
    - "8000:8000"
  volumes:
    - ./docs:/docs
  networks:
    - mynetwork
  entrypoint: ["mkdocs", "serve", "-a", "0.0.0.0:8000"]
Crear y organizar la documentación en archivos Markdown dentro del directorio ./docs.
Comando para iniciar MkDocs:
bash
Copiar código
docker-compose up -d mkdocs
Acceso a la documentación en http://localhost:8000.
7. Integración de Jupyter Notebook
Fecha: [Fecha de configuración]
Razón: Facilitar la experimentación y el desarrollo interactivo.
Pasos Tomados:
Configuración de Jupyter en docker-compose.yml:
yaml
Copiar código
jupyter:
  image: jupyter/pyspark-notebook:latest
  ports:
    - "8888:8888"
  networks:
    - mynetwork
  volumes:
    - ./notebooks:/home/jovyan/work
Comando para iniciar Jupyter:
bash
Copiar código
docker-compose up -d jupyter
Acceso a Jupyter Notebook en http://localhost:8888.
8. Incorporación de Otras Librerías de NLP: Transformers y Torch
Fecha: [Fecha de incorporación]
Acción: Decisión de incluir transformers y torch para ampliar las capacidades de NLP.
Pasos Tomados:
Actualizar requirements.txt:
text
Copiar código
spacy
transformers
torch
Modificar Dockerfile para incluir las nuevas dependencias:
Dockerfile
Copiar código
FROM apache/airflow:2.10.0
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
9. Construcción y Ejecución de Contenedores
Fecha: [Fecha de ejecución]
Acción: Construir y desplegar los contenedores con las configuraciones actualizadas.
Comandos:
Construcción de imágenes:
bash
Copiar código
docker-compose build
Iniciar todos los servicios:
bash
Copiar código
docker-compose up -d
10. Pruebas y Verificación
Fecha: [Fecha de pruebas]
Acción: Verificar que todos los servicios funcionen correctamente.
Resultados:
Airflow: Acceso exitoso a http://localhost:8080.
Metabase: Acceso exitoso a http://localhost:3000.
Jupyter Notebook: Acceso exitoso a http://localhost:8888.
MkDocs: Documentación accesible en http://localhost:8000.
Observaciones: Todos los servicios están en estado running y funcionando como se esperaba.
11. Notas Futuros y Escalabilidad
Fecha: [Fecha de nota]
Acción: Documentar consideraciones para la escalabilidad futura.
Notas:
Considerar la integración de procesamiento distribuido si aumenta significativamente el volumen de datos.
Evaluar el uso de versiones más avanzadas de modelos de NLP conforme se necesiten tareas más complejas.
Mantener la documentación y los notebooks organizados y actualizados para facilitar la colaboración y el mantenimiento.
Conclusión del Seguimiento
El proyecto ha avanzado de acuerdo con los objetivos planteados, ajustando las herramientas y tecnologías en base a la compatibilidad y las necesidades específicas del proyecto. La decisión de usar spaCy, transformers y torch en lugar de un clúster de Spark simplifica la configuración y permite un procesamiento efectivo de NLP sin necesidad de infraestructura compleja. La inclusión de Jupyter Notebook y MkDocs facilita el desarrollo y la documentación, mejorando la transparencia y la colaboración en el proyecto.
