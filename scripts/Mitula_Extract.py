import os
import re
import csv

# Función para limpiar el texto y eliminar espacios innecesarios
def limpiar_texto(texto):
    return ' '.join(texto.split()) if texto else 'N/A'

# Función para buscar los archivos que empiezan con "Mitula"
def buscar_archivos_txt(carpeta):
    archivos_txt = [f for f in os.listdir(carpeta) if f.startswith('Mitula') and f.endswith('.txt')]
    return archivos_txt

# Función para procesar los archivos y convertirlos a CSV
def procesar_archivo_txt_a_csv(archivo_txt, carpeta_txt, carpeta_csv):
    with open(os.path.join(carpeta_txt, archivo_txt), 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Expresiones regulares para extraer datos clave del contenido del archivo txt
    pattern_precio = re.compile(r'(\$\s?\d+(?:,\d+)*(?:\.\d+)?)')  # Buscar precios como $150,000
    pattern_ubicacion = re.compile(r'data-location="([^"]+)"')  # Ubicación
    pattern_area = re.compile(r'data-floorarea="([^"]+)"')  # Área en m²
    pattern_habitaciones = re.compile(r'data-rooms="(\d+)"')  # Habitaciones
    pattern_banos = re.compile(r'data-test="bathrooms">\s*(\d+)')  # Baños
    pattern_tipo_propiedad = re.compile(r'badge-container__property-type">\s*(\w+)')  # Tipo de propiedad
    pattern_descripcion = re.compile(r'class="listing-card__title"[^>]*>([^<]+)</div>')  # Título de la propiedad
    pattern_instalaciones = re.compile(r'facility-item__text">\s*(.*?)\s*</span>')  # Instalaciones o comodidades
    pattern_agente = re.compile(r'class="published-date">\s*(.*?)\s*</span>')  # Nombre del agente
    pattern_url_imagenes = re.compile(r'src="(https://img.mitula.com/[^"]+)"')  # Imágenes de la propiedad

    # Obtener el nombre del archivo CSV de salida
    archivo_csv = os.path.join(carpeta_csv, archivo_txt.replace('raw_', '').replace('.txt', '.csv'))

    # Escribir en el archivo CSV
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        campos = ['Precio', 'Ubicación', 'Área (m²)', 'Habitaciones', 'Baños', 'Tipo de propiedad', 
                  'Descripción', 'Instalaciones', 'Agente', 'Imágenes']
        escritor_csv = csv.DictWriter(csvfile, fieldnames=campos, delimiter='|')
        escritor_csv.writeheader()

        # Extraer los datos usando patrones y expresiones regulares
        precios = pattern_precio.findall(contenido)
        ubicaciones = pattern_ubicacion.findall(contenido)
        areas = pattern_area.findall(contenido)
        habitaciones = pattern_habitaciones.findall(contenido)
        banos = pattern_banos.findall(contenido)
        tipos_propiedad = pattern_tipo_propiedad.findall(contenido)
        descripciones = pattern_descripcion.findall(contenido)
        instalaciones = pattern_instalaciones.findall(contenido)
        agentes = pattern_agente.findall(contenido)
        imagenes = pattern_url_imagenes.findall(contenido)

        # Asegurar que las listas tengan el mismo tamaño, rellenar con 'N/A' si falta algún valor
        max_length = max(len(precios), len(ubicaciones), len(areas), len(habitaciones), len(banos), len(tipos_propiedad), len(descripciones), len(instalaciones), len(agentes), len(imagenes))
        precios += ['N/A'] * (max_length - len(precios))
        ubicaciones += ['N/A'] * (max_length - len(ubicaciones))
        areas += ['N/A'] * (max_length - len(areas))
        habitaciones += ['N/A'] * (max_length - len(habitaciones))
        banos += ['N/A'] * (max_length - len(banos))
        tipos_propiedad += ['N/A'] * (max_length - len(tipos_propiedad))
        descripciones += ['N/A'] * (max_length - len(descripciones))
        instalaciones += ['N/A'] * (max_length - len(instalaciones))
        agentes += ['N/A'] * (max_length - len(agentes))
        imagenes += ['N/A'] * (max_length - len(imagenes))

        # Escribir cada fila en el CSV
        for i in range(max_length):
            escritor_csv.writerow({
                'Precio': limpiar_texto(precios[i]),
                'Ubicación': limpiar_texto(ubicaciones[i]),
                'Área (m²)': limpiar_texto(areas[i]),
                'Habitaciones': limpiar_texto(habitaciones[i]),
                'Baños': limpiar_texto(banos[i]),
                'Tipo de propiedad': limpiar_texto(tipos_propiedad[i]),
                'Descripción': limpiar_texto(descripciones[i]),
                'Instalaciones': limpiar_texto(", ".join(instalaciones)),
                'Agente': limpiar_texto(agentes[i]),
                'Imágenes': limpiar_texto(imagenes[i])
            })

    print(f"Datos convertidos a CSV: {archivo_csv}")

# Función principal para convertir todos los archivos txt a CSV
def convertir_txt_a_csv():
    carpeta_txt = 'data/output'
    carpeta_csv = 'data/csv'
    
    # Crear carpeta CSV si no existe
    os.makedirs(carpeta_csv, exist_ok=True)
    
    # Buscar todos los archivos .txt en la carpeta de salida
    archivos_txt = buscar_archivos_txt(carpeta_txt)
    
    for archivo_txt in archivos_txt:
        procesar_archivo_txt_a_csv(archivo_txt, carpeta_txt, carpeta_csv)

# Uso de ejemplo
if __name__ == "__main__":
    convertir_txt_a_csv()
