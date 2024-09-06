## Documentación de Instalación y Configuración: Docker, Airflow, Metabase, y Entorno Virtual para requirements.txt
Esta guía detalla los pasos necesarios para instalar Docker, configurar Airflow y Metabase usando Docker Compose, y crear un entorno virtual en Python para gestionar las dependencias del proyecto.

## 1. Instalación de Docker
##    1.1. Instalar Docker
        1- Actualizar los repositorios de apt:
            sudo apt-get update
        
        2- Instalar paquetes necesarios:
            sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
        
        3- Añadir la clave GPG de Docker:
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

        4- Añadir el repositorio de Docker a apt:
            sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        
        5- Actualizar los repositorios de apt de nuevo:
            sudo apt-get update
        
        6- Instalar Docker Community Edition:
            sudo apt-get install docker-ce
        
        7- Verificar la instalación de Docker:
            docker --version
            * Debería mostrar la versión de Docker instalada.

##  1.2. Configurar permisos para Docker
    1- Añadir tu usuario al grupo docker para evitar usar sudo cada vez que se ejecuta un comando Docker:
        sudo usermod -aG docker $USER
    
    2- Aplicar cambios (puede ser necesario reiniciar la sesión):
        newgrp docker

## 2. Instalación de Docker Compose
    1- Descargar Docker Compose:
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    2- Aplicar permisos ejecutables:
        sudo chmod +x /usr/local/bin/docker-compose
    
    3- Verificar la instalación de Docker Compose:
        docker-compose --version
        * Debería mostrar la versión de Docker Compose instalada.

## 3. Configuración de Airflow y Metabase con Docker Compose
##    3.1. Crear el Archivo .env
    Crea un archivo .env en el directorio del proyecto con las siguientes variables de entorno:
        POSTGRES_DB=tfb
        POSTGRES_USER=edi
        POSTGRES_PASSWORD=POSTGRES_PASSWORD**
        AIRFLOW_ADMIN_USER=admin
        AIRFLOW_ADMIN_PASSWORD=AIRFLOW_ADMIN_PASSWORD**
        AIRFLOW_ADMIN_EMAIL=edisson.reyes.data@gmail.com

##  3.2. Crear el Archivo docker-compose.yml
    Crea un archivo docker-compose.yml en el mismo directorio con el siguiente contenido:
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

        airflow-webserver:
            image: apache/airflow:2.7.0-python3.9
            container_name: airflow-webserver
            environment:
            - AIRFLOW__CORE__LOAD_EXAMPLES=False
            - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
            ports:
            - "8085:8080"
            volumes:
            - ./dags:/opt/airflow/dags
            command: "airflow webserver"
            depends_on:
            - postgres

        airflow-scheduler:
            image: apache/airflow:2.7.0-python3.9
            container_name: airflow-scheduler
            environment:
            - AIRFLOW__CORE__LOAD_EXAMPLES=False
            - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
            volumes:
            - ./dags:/opt/airflow/dags
            command: "airflow scheduler"
            depends_on:
            - postgres

##  3.3. Levantar los Servicios
    1- Iniciar Docker Compose:
    Navega al directorio del proyecto donde se encuentra el archivo docker-compose.yml y ejecuta:
        docker-compose up -d

    2- Verificar que los Contenedores estén Corriendo:
        docker ps
        * Deberías ver los contenedores para postgres, airflow-webserver, airflow-scheduler en ejecución.

## 4. Creación de un Entorno Virtual para requirements.txt
##  4.1. Crear el Entorno Virtual
    1- Navegar al Directorio del Proyecto:
        cd ~/Descargas/proyecto_tfb
        
    2- Crear un Entorno Virtual:
            python3 -m venv venv
        
    3- Activar el Entorno Virtual:
            source venv/bin/activate
            * Ahora deberías ver (venv) al principio de tu línea de comandos, indicando que el entorno virtual está activo.

##  4.2. Gestionar Dependencias con requirements.txt
    1- Crear un Archivo requirements.txt:
    Dentro del directorio del proyecto, crea o edita el archivo requirements.txt con las dependencias necesarias. Para este proyecto, puedes listar las dependencias básicas:
        apache-airflow==2.7.0
        apache-airflow-providers-postgres

    2- Instalar Dependencias:
    Con el entorno virtual activado, instala las dependencias listadas en requirements.txt:
        pip install -r requirements.txt

##  4.3. Documentar Dependencias
    1- Congelar Dependencias:
    Para registrar todas las dependencias con sus versiones específicas, ejecuta:
        pip freeze > requirements.txt
        * Esto actualizará el archivo requirements.txt con todas las dependencias actuales.

## 5. Verificación de la Configuración
1- Acceder a Airflow: Abre http://localhost:8085 en tu navegador. Usa las credenciales definidas en el archivo .env.
2- Acceder a Metabase: Abre http://localhost:3000 para configurar Metabase.

## 6. Subir Cambios a GitHub
1- Agregar Archivos a Git:
    git add .

2- Hacer Commit de los Cambios:
    git commit -m "Configuración inicial de Docker, Airflow y Metabase con entorno virtual"

3- Subir Cambios a GitHub:
    git push origin main

## Conclusión
Estos pasos proporcionan una configuración básica y una guía de inicio para trabajar con Airflow Y PostgreSQL utilizando Docker y Docker Compose, además de manejar dependencias con un entorno virtual
