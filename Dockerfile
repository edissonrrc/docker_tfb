# Dockerfile

# Utiliza la imagen oficial de Apache Airflow con Python 3.9
FROM apache/airflow:2.7.0-python3.9

# Actualiza pip a la última versión
RUN pip install --upgrade pip

# Copia el archivo de dependencias adicionales (si existe) y ejecuta su instalación.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia los DAGs, scripts y plugins personalizados al contenedor de Airflow.
COPY dags/ $AIRFLOW_HOME/dags/
COPY scripts/ $AIRFLOW_HOME/scripts/
COPY plugins/ $AIRFLOW_HOME/plugins/
COPY images/ $AIRFLOW_HOME/images/
COPY data/ $AIRFLOW_HOME/data/
COPY flask/ $AIRFLOW_HOME/flask/

# Asignar permisos de acceso a los directorios copiados.
USER root
RUN chmod -R 755 $AIRFLOW_HOME/dags && \
    chmod -R 755 $AIRFLOW_HOME/scripts && \
    chmod -R 755 $AIRFLOW_HOME/plugins && \
    chmod -R 755 $AIRFLOW_HOME/images && \
    chmod -R 755 $AIRFLOW_HOME/data && \
    chmod -R 755 $AIRFLOW_HOME/flask

# Crear un grupo compartido y asignar permisos.
RUN groupadd -g 1001 sharedgroup && \
    usermod -aG sharedgroup airflow

RUN chown -R :sharedgroup $AIRFLOW_HOME/images && \
    chmod -R 775 $AIRFLOW_HOME/images

RUN chown -R :sharedgroup $AIRFLOW_HOME/data && \
    chmod -R 775 $AIRFLOW_HOME/data

RUN chown -R :sharedgroup $AIRFLOW_HOME/flask && \
    chmod -R 775 $AIRFLOW_HOME/flask

# Cambia el usuario activo de vuelta a 'airflow' para ejecutar Airflow de manera no privilegiada.
USER airflow

# Ejecutar el comando airflow db migrate antes de iniciar el servidor web o el scheduler
CMD bash -c "airflow db migrate && airflow webserver"

