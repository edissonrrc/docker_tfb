# Dockerfile

# Utiliza la imagen oficial de Apache Airflow con Python 3.9
# Esta imagen base proporciona un entorno listo para ejecutar Airflow con todas las dependencias preinstaladas.
FROM apache/airflow:2.7.0-python3.9

# Copia el archivo de dependencias adicionales (si existe) y ejecuta su instalación.
# Este paso es útil cuando se requieren paquetes de Python adicionales específicos para las tareas de Airflow.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia los DAGs, scripts y plugins personalizados al contenedor de Airflow.
# Esto asegura que los flujos de trabajo (DAGs) y cualquier código personalizado (scripts, plugins) estén disponibles en el entorno de ejecución.
COPY dags/ $AIRFLOW_HOME/dags/
COPY scripts/ $AIRFLOW_HOME/scripts/
COPY plugins/ $AIRFLOW_HOME/plugins/
COPY images/ $AIRFLOW_HOME/images/

# Asignar permisos de acceso a los directorios copiados.
# '755' otorga permisos de lectura y ejecución para todos, y permisos de escritura solo para el propietario (usuario 'airflow').
USER root
RUN chmod -R 755 $AIRFLOW_HOME/dags && \
    chmod -R 755 $AIRFLOW_HOME/scripts && \
    chmod -R 755 $AIRFLOW_HOME/plugins && \
    chmod -R 755 $AIRFLOW_HOME/images

# Crear un grupo compartido 'sharedgroup' con el GID 1001, si no existe.
# Añadir el usuario 'airflow' al grupo para permitir la colaboración en el directorio compartido 'images'.
RUN groupadd -g 1001 sharedgroup && \
    usermod -aG sharedgroup airflow

# Cambiar el grupo propietario de la carpeta 'images' a 'sharedgroup'.
# Se asignan permisos '775' para otorgar acceso de escritura tanto al propietario como al grupo,
# permitiendo que tanto 'airflow' como miembros del grupo 'sharedgroup' colaboren en esta carpeta.
RUN chown -R :sharedgroup $AIRFLOW_HOME/images && \
    chmod -R 775 $AIRFLOW_HOME/images

# Cambia el usuario activo de vuelta a 'airflow' para ejecutar Airflow de manera no privilegiada.
# Esta es una práctica recomendada para ejecutar procesos de manera segura.
USER airflow

# Comando predeterminado para iniciar el servidor web de Airflow.
# Esto lanza el servidor web en el puerto 8080 (puerto por defecto de Airflow), lo cual facilita el acceso a la interfaz web.
CMD ["airflow", "webserver"]

