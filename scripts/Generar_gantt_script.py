import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import os
from datetime import datetime

# Definir la ruta del directorio donde se guardarán las imágenes
images_dir = '/opt/airflow/images'

# Crear la carpeta "images" si no existe
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Datos del proyecto con fases e hitos
data = {
    'Tarea': [
        'Fase Preparatoria y Configuraciones Iniciales',
        'Hito 1: Preparación del Entorno',
        'Hito 2: Configuración Inicial del Proyecto',
        'Hito 3: Crear y Configurar el Archivo .env',
        'Hito 4: Configuración Inicial de Docker Compose',
        'Hito 5: Configuración Completa de Docker Compose',
        'Hito 6: Crear Entorno Virtual de Python',
        'Hito 7: Configuración de Airflow',
        'Hito 8: Configuración de Metabase',
        'Hito 9: Documentación Inicial y Propuesta del Proyecto',
        'Entrega 1: Fundamentos de la propuesta',
        'Hito 10: Desarrollo de DAGs de Producción',
        'Hito 11: Desarrollo de Funcionalidades de Análisis de Texto',
        'Hito 12: Revisión y Ajustes de Propuesta',
        'Entrega 2: Aplicación de la Metodología y Primeros Resultados',
        'Hito 13: Implementación de Análisis de Segmentación de Mercado',
        'Hito 14: Desarrollo de Modelos Predictivos Iniciales',
        'Hito 15: Revisión de Resultados y Ajustes en Modelos Predictivos',
        'Entrega 3: Resultados y Documentación Avanzada',
        'Hito 16: Implementación de Modelos Predictivos Avanzados',
        'Hito 17: Análisis de Resultados y Ajustes Finales',
        'Hito 18: Preparación de la Memoria',
        'Hito 19: Análisis de Sensibilidad y Elasticidad del Precio',
        'Hito 20: Ajustes Finales y Validación Completa',
        'Hito 21: Documentación Completa del Proyecto',
        'Entrega Final del Proyecto',
        'Hito 22: Preparación y Presentación Final',
        'Hito 23: Ajustes Finales basados en Retroalimentación del Tutor',
        'Depósito TFB'
    ],
    'Inicio': [
        '2024-05-18', '2024-05-18', '2024-06-08', '2024-06-13', '2024-06-14',
        '2024-06-23', '2024-06-25', '2024-07-10', '2024-07-11', '2024-07-12',
        '2024-07-16', '2024-07-16', '2024-07-20', '2024-07-23', '2024-07-23',
        '2024-07-23', '2024-07-26', '2024-07-29', '2024-08-12', '2024-08-12',
        '2024-08-16', '2024-08-23', '2024-09-04', '2024-09-08', '2024-09-11',
        '2024-09-02', '2024-09-12', '2024-09-15', '2024-09-16'
    ],
    'Fin': [
        '2024-06-29', '2024-06-08', '2024-06-12', '2024-06-13', '2024-06-22',
        '2024-06-24', '2024-07-10', '2024-07-11', '2024-07-12', '2024-07-15',
        '2024-07-22', '2024-07-20', '2024-07-22', '2024-07-23', '2024-08-11',
        '2024-07-26', '2024-07-29', '2024-08-11', '2024-09-01', '2024-08-16',
        '2024-08-22', '2024-09-03', '2024-09-07', '2024-09-10', '2024-09-12',
        '2024-09-15', '2024-09-14', '2024-09-15', '2024-09-23'
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
colors = ['#FFDDC1', '#FFABAB', '#FFC3A0', '#C1FFDD', '#ABFFAB', '#A0FFC3']

# Rellenar el fondo de los meses
start_month = pd.Timestamp('2024-05-18')
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
    elif 'Fase' in tarea or 'Entrega' in tarea:
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
ax.set_title('Diagrama de Gantt del Proyecto de TFB', fontsize=14, fontweight='bold', color='darkblue')

# Mejorar presentación
ax.set_facecolor('#f9f9f9')
ax.invert_yaxis()

# Alinear el texto a la izquierda, ajustar la posición y usar formato negrita
for label in ax.get_yticklabels():
    tarea_text = label.get_text()
    if 'Fase' in tarea_text or 'Depósito TFB' in tarea_text or 'Entrega' in tarea_text:
        label.set_fontweight('bold')
    label.set_horizontalalignment('right')
    label.set_x(-0.05)

# Añadir una marca de agua en la esquina inferior derecha con la hora y fecha actuales
creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
fig.text(0.95, 0.01, f'Edisson Reyes - Diagrama creado el {creation_time}', fontsize=12, color='gray', ha='right', va='bottom', alpha=0.5)

# Guardar la imagen en la carpeta "images"
output_path = os.path.join(images_dir, 'gantt_tfb.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')

print(f"Saving image to: {output_path}")
