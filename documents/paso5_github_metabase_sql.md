Documentación del Progreso Mestabase y consultas sql con recuperacion de servidor por incompatibilidades. 
1. Resumen del Proyecto
El proyecto tiene como objetivo analizar datos de propiedades inmobiliarias en Quito, Ecuador, para obtener insights sobre los precios de las propiedades, su distribución geográfica, y características de las propiedades (tamaño, número de habitaciones, baños, etc.). Los datos se almacenan en una base de datos PostgreSQL, se visualizan y analizan en Metabase, y se automatizan ciertos análisis usando Airflow.
2. Configuración Inicial y Problemas Encontrados
2.1 Configuración Inicial:
    • Repositorio GitHub: Se clonó el repositorio inicial del proyecto desde GitHub. Durante la fase inicial, encontramos problemas de incompatibilidad con algunos paquetes.
    • Recuperación de Versiones Estables: Debido a los problemas de incompatibilidad, fue necesario recuperar el estado del proyecto utilizando comandos de Git para volver a una versión estable.
      Comando utilizado:
      bash
      Copiar código
      git reset --hard <hash_de_confirmacion>
      Donde <hash_de_confirmacion> corresponde a la versión estable previamente confirmada.
2.2 Configuración del Entorno:
    • Se decidió usar contenedores Docker para estandarizar el entorno de desarrollo y ejecución:
        ◦ PostgreSQL para almacenar datos.
        ◦ Metabase para visualización de datos.
        ◦ Airflow para orquestación de procesos y automatización de análisis.
    • Contenedores en Uso:
        ◦ postgres: Servidor de base de datos PostgreSQL.
        ◦ metabase: Herramienta de visualización de datos.
        ◦ airflow-webserver y airflow-scheduler: Servidores para la orquestación de procesos.
3. Configuración de Metabase
3.1 Conectar Metabase a PostgreSQL:
    1. Acceder a la interfaz de Metabase:
        ◦ URL: http://localhost:3000
    2. Agregar una nueva base de datos:
        ◦ Desde Admin -> Databases, se agregó PostgreSQL como base de datos con los siguientes parámetros:
            ▪ Host: postgres (nombre del contenedor).
            ▪ Port: 5432.
            ▪ Database name: nombre_base_datos.
            ▪ Username: usuario.
            ▪ Password: contraseña.
    3. Problemas Encontrados y Soluciones:
        ◦ Inicialmente, hubo problemas de conexión entre Metabase y PostgreSQL. Aseguramos que ambos contenedores estuvieran en la misma red Docker para permitir la comunicación directa.
3.2 Primeras Consultas SQL en Metabase:
    • Se realizaron consultas básicas para explorar los datos disponibles y familiarizarse con la estructura de la base de datos.
      Ejemplo de consulta para ver todas las propiedades:
      sql
      Copiar código
      SELECT * FROM propiedades LIMIT 10;
    • Se crearon visualizaciones simples para empezar a entender la distribución de los datos.
4. Análisis Sugeridos y Planificación
4.1 Análisis de Precios por Metro Cuadrado (M2) por Ubicación:
    • Propósito: Entender cómo varía el precio de las propiedades por metro cuadrado en diferentes ubicaciones.
    • Herramienta: Metabase.
    • Consulta SQL:
      sql
      Copiar código
      SELECT 
          "Ubicacion", 
          AVG("Precio M2") as precio_m2_promedio
      FROM 
          propiedades
      GROUP BY 
          "Ubicacion"
      ORDER BY 
          precio_m2_promedio DESC;
    • Visualización: Gráfico de barras.
4.2 Distribución de Propiedades por Número de Habitaciones y Baños:
    • Propósito: Analizar las características más comunes de las propiedades disponibles.
    • Herramienta: Metabase.
    • Consulta SQL:
      sql
      Copiar código
      SELECT 
          "Habitaciones", 
          "Banos", 
          COUNT(*) as numero_propiedades
      FROM 
          propiedades
      GROUP BY 
          "Habitaciones", 
          "Banos"
      ORDER BY 
          "Habitaciones", 
          "Banos";
    • Visualización: Gráfico de barras apiladas o heatmap.
4.3 Evolución de Precios de Publicación a lo Largo del Tiempo:
    • Propósito: Identificar tendencias temporales en los precios de las propiedades.
    • Herramienta: Metabase.
    • Consulta SQL:
      sql
      Copiar código
      SELECT 
          "Fecha Captura", 
          AVG("Precio") as precio_promedio
      FROM 
          propiedades
      GROUP BY 
          "Fecha Captura"
      ORDER BY 
          "Fecha Captura";
    • Visualización: Gráfico de líneas.
4.4 Identificación de Propiedades con Precios Fuera del Rango Normal:
    • Propósito: Detectar propiedades cuyo precio es significativamente diferente del promedio en su área.
    • Herramienta: Metabase.
    • Consulta SQL Completa con subconsulta para calcular desviaciones:
      sql
      Copiar código
      WITH precios_ubicacion AS (
          SELECT 
              "Ubicacion",
              AVG("Precio M2") as precio_m2_promedio
          FROM 
              propiedades
          GROUP BY 
              "Ubicacion"
      )
      SELECT 
          t.*,
          precios_ubicacion.precio_m2_promedio,
          ("Precio M2" - precios_ubicacion.precio_m2_promedio) as desviacion_precio_m2
      FROM 
          propiedades t
      JOIN 
          precios_ubicacion 
      ON 
          t."Ubicacion" = precios_ubicacion."Ubicacion"
      WHERE 
          ABS("Precio M2" - precio_m2_promedio) > precio_m2_promedio * 0.2  -- 20% de desviación como umbral
      ORDER BY 
          desviacion_precio_m2 DESC;
    • Visualización: Gráfico de dispersión con líneas de referencia.
5. Automatización de Análisis con Airflow
5.1 Estructura del DAG:
    • Tareas Definidas:
        ◦ extract_data: Extrae datos desde PostgreSQL.
        ◦ analyze_data: Ejecuta consultas SQL para realizar los análisis previamente definidos.
        ◦ generate_reports: Opcionalmente, genera y envía informes basados en los resultados del análisis.
5.2 Ejemplo de DAG:
python
Copiar código
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email import EmailOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 29),
    'retries': 1,
}

dag = DAG(
    'analyze_real_estate_data',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
)

# Task para ejecutar la consulta de análisis de precios por m2 por ubicación
analyze_prices_task = PostgresOperator(
    task_id='analyze_prices',
    postgres_conn_id='postgres_default',
    sql='''-- Inserta aquí la consulta SQL correspondiente --''',
    dag=dag,
)

# Task para enviar un correo electrónico con los resultados (opcional)
send_email_task = EmailOperator(
    task_id='send_email',
    to='example@example.com',
    subject='Resultados del Análisis de Propiedades',
    html_content='Los resultados del análisis están listos.',
    dag=dag,
)

# Definir dependencias
analyze_prices_task >> send_email_task
6. Conclusiones y Próximos Pasos
    • Próximos Pasos:
        ◦ Refinar los análisis y visualizaciones en Metabase según los nuevos insights que surjan.
        ◦ Continuar automatizando el análisis y la generación de informes mediante Airflow.
        ◦ Implementar alertas basadas en ciertos umbrales de datos detectados para identificar oportunidades o riesgos de inversión.
    • Conclusión: Este proyecto ha permitido una comprensión más profunda del mercado inmobiliario en Quito, y ha establecido una base sólida para la toma de decisiones informadas sobre inversiones en bienes raíces. Continuaremos iterando y mejorando los análisis con base en los resultados obtenidos.
Esta documentación proporciona un registro claro de los pasos realizados y puede servir como guía para futuras mejoras y expansiones del proyecto. Si hay cambios significativos o nuevas funcionalidades añadidas, se debe actualizar esta documentación en consecuencia.

