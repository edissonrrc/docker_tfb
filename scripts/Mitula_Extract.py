import os
import re
import csv

# Función para limpiar el texto y eliminar espacios innecesarios
def limpiar_texto(texto):
    return ' '.join(texto.split()) if texto else 'N/A'

# Función para extraer solo los números de una cadena
def extraer_numeros(texto):
    return re.sub(r'[^\d]', '', texto)

# Función para limpiar la ubicación y eliminar "Pichincha"
def limpiar_ubicacion(ubicacion):
    return ubicacion.replace(', Pichincha', '').strip()

# Función para buscar los archivos que empiezan con "Mitula"
def buscar_archivos_txt(carpeta):
    archivos_txt = [f for f in os.listdir(carpeta) if f.startswith('Mitula') and f.endswith('.txt')]
    return archivos_txt

# Función para procesar los archivos y convertirlos a CSV
def procesar_archivo_txt_a_csv(archivo_txt, carpeta_txt, carpeta_csv):
    with open(os.path.join(carpeta_txt, archivo_txt), 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Expresiones regulares para extraer datos clave del contenido del archivo txt
    pattern_precio = re.compile(r'data-price="([^"]+)"')  # Buscar precios
    pattern_ubicacion = re.compile(r'data-location="([^"]+)"')  # Ubicación
    pattern_area = re.compile(r'data-floorarea="([^"]+)"')  # Área en m²
    pattern_habitaciones = re.compile(r'data-rooms="(\d+)"')  # Habitaciones
    pattern_banos = re.compile(r'data-test="bathrooms">\s*(\d+)')  # Número de baños
    pattern_nombre_agencia = re.compile(r'data-nombreagencia="([^"]+)"')  # Nombre de la agencia
    pattern_titulo = re.compile(r'class="listing-card__title"[^>]*>([^<]+)</div>')  # Título de la propiedad
    pattern_instalaciones = re.compile(r'class="facility-item__text">\s*(.*?)\s*</span>')  # Instalaciones

    # Obtener el nombre del archivo CSV de salida
    archivo_csv = os.path.join(carpeta_csv, archivo_txt.replace('_raw', '').replace('.txt', '.csv'))

    # Escribir en el archivo CSV
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        campos = ['Precio', 'Área (m²)', 'Ubicación', 'Habitaciones', 'Baños', 'Nombre de la agencia', 'Título de la propiedad', 'Instalaciones']
        escritor_csv = csv.DictWriter(csvfile, fieldnames=campos, delimiter='|')
        escritor_csv.writeheader()

        # Extraer los datos usando patrones y expresiones regulares
        precios = pattern_precio.findall(contenido)
        ubicaciones = pattern_ubicacion.findall(contenido)
        areas = pattern_area.findall(contenido)
        habitaciones = pattern_habitaciones.findall(contenido)
        banos = pattern_banos.findall(contenido)
        nombres_agencia = pattern_nombre_agencia.findall(contenido)
        titulos = pattern_titulo.findall(contenido)
        # Extraer todas las instalaciones de las propiedades
        lista_instalaciones = [pattern_instalaciones.findall(propiedad) for propiedad in re.split(r'<div class="listing listing-card"', contenido)]

        # Asegurar que las listas tengan el mismo tamaño, rellenar con 'N/A' si falta algún valor
        max_length = max(len(precios), len(ubicaciones), len(areas), len(habitaciones), len(banos), len(nombres_agencia), len(titulos))
        precios += ['N/A'] * (max_length - len(precios))
        ubicaciones += ['N/A'] * (max_length - len(ubicaciones))
        areas += ['N/A'] * (max_length - len(areas))
        habitaciones += ['N/A'] * (max_length - len(habitaciones))
        banos += ['N/A'] * (max_length - len(banos))
        nombres_agencia += ['N/A'] * (max_length - len(nombres_agencia))
        titulos += ['N/A'] * (max_length - len(titulos))
        lista_instalaciones += [[]] * (max_length - len(lista_instalaciones))  # Ajusta el tamaño de la lista de instalaciones

        # Escribir cada fila en el CSV
        for i in range(max_length):
            instalaciones_combinadas = ', '.join(lista_instalaciones[i]) if lista_instalaciones[i] else 'N/A'
            escritor_csv.writerow({
                'Precio': extraer_numeros(precios[i]),  # Extraer solo números del precio
                'Área (m²)': extraer_numeros(areas[i]),  # Extraer solo números del área
                'Ubicación': limpiar_ubicacion(ubicaciones[i]),  # Limpiar ubicación para eliminar "Pichincha"
                'Habitaciones': limpiar_texto(habitaciones[i]),
                'Baños': limpiar_texto(banos[i]),
                'Nombre de la agencia': limpiar_texto(nombres_agencia[i]),
                'Título de la propiedad': limpiar_texto(titulos[i]),
                'Instalaciones': limpiar_texto(instalaciones_combinadas)
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
