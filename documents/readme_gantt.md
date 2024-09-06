cat << 'EOF' > README.md
# Diagrama de Gantt para el Proyecto de Modelado Predictivo de Asequibilidad de Vivienda

Este proyecto genera un diagrama de Gantt que visualiza las fases y los hitos del proyecto de modelado predictivo de la asequibilidad de vivienda en Quito. El diagrama se guarda automáticamente en la carpeta `images` como `gantt_tfb.png`.

## Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Requisitos](#requisitos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Cómo Ejecutar el Proyecto](#cómo-ejecutar-el-proyecto)
- [Ejemplo de Uso](#ejemplo-de-uso)

## Descripción del Proyecto

El propósito de este proyecto es crear un gráfico de Gantt que represente visualmente el cronograma de un proyecto de análisis y modelado predictivo. El gráfico incluye las fases principales, hitos, y el depósito final del proyecto. Además, el gráfico se guarda automáticamente en formato PNG con alta resolución.

## Requisitos

Para ejecutar este proyecto, necesitas tener instalados los siguientes paquetes de Python:

- `matplotlib`
- `pandas`

Puedes instalar estos paquetes utilizando `pip`:

pip install matplotlib pandas


## Estructura del Proyecto

El proyecto tiene la siguiente estructura de directorios:

.
├── images/                     # Carpeta donde se guardan las imágenes generadas
├── gantt.py                    # Código fuente para generar el gráfico de Gantt
└── readme_gantt.md             # Documentación del proyecto


## Cómo Ejecutar el Proyecto

1. Clona este repositorio en tu máquina local.
2. Instala los requisitos utilizando el comando pip mencionado anteriormente.
3. Ejecuta el script gantt.py. Esto generará el gráfico de Gantt y lo guardará en la carpeta images.

python gantt.py

4. Revisa la carpeta images para ver el gráfico generado (gantt_tfb.png).

## Ejemplo de Uso

El gráfico de Gantt generado muestra las siguientes características:

- Fases del Proyecto: Se destacan en negrita y color verde claro.
- Hitos del Proyecto: Se muestran en color azul claro.
- Depósito TFB: Aparece con mayor grosor y en color azul oscuro.
- Relleno de Meses: Cada mes está suavemente coloreado en el fondo del gráfico.
- Formato de Fechas: Los días se muestran en intervalos de 3 días.

## Hitos Clave Representados:
1. Fase Preparatoria y Configuraciones Iniciales: Desde el 18 de mayo hasta el 15 de junio de 2024, incluyendo la configuración del entorno, proyecto, y herramientas necesarias como Docker, Airflow y Metabase.
2. Entrega Parcial 1: Completa el 22 de julio de 2024, cubriendo los fundamentos de la propuesta y las configuraciones iniciales.
3. Análisis Exploratorio y Desarrollo Inicial: Del 16 de junio al 11 de agosto de 2024, incluyendo el desarrollo de DAGs de producción y modelos predictivos iniciales.
4. Entrega Parcial 2: Finaliza el 11 de agosto de 2024, con resultados preliminares y análisis iniciales.
5. Avances en Modelos Predictivos y Análisis Avanzado: Desde el 12 de agosto hasta el 31 de agosto de 2024, desarrollando modelos avanzados y técnicas de análisis de datos.
6. Entrega Parcial 3: Finalización el 31 de agosto de 2024, incluyendo un avance significativo en la documentación y análisis del proyecto.
7. Finalización y Preparación para la Entrega Final: Del 1 de septiembre al 15 de septiembre de 2024, centrado en la validación final, ajustes y preparación de la documentación completa del proyecto.
8. Depósito TFB y Defensa Final: Programado para el 23 de septiembre de 2024, culminando con la defensa del proyecto.
