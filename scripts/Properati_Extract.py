import os
import re
import csv
from bs4 import BeautifulSoup

def limpiar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

def extraer_numeros(texto):
    """Extrae solo los números de un texto"""
    numeros = re.findall(r'\d+', texto)
    return ''.join(numeros) if numeros else 'N/A'

# Función para procesar el archivo de texto y extraer los datos
def procesar_txt_a_csv(archivo_txt, archivo_csv):
    with open(archivo_txt, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    soup = BeautifulSoup(contenido, 'html.parser')
    propiedades = soup.find_all("div", {"class": "listing-card__information"})
    
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        escritor_csv = csv.writer(csvfile, delimiter='|')
        # Escribir encabezado con los campos relevantes (sin Título ni Etiqueta Proyecto)
        escritor_csv.writerow([
            'Precio', 
            'Ubicación', 
            'Área', 
            'Habitaciones', 
            'Baños', 
            'Agencia', 
            'Fecha Publicación'
        ])

        for propiedad in propiedades:
            # Extraer etiqueta de proyecto y excluir si es "PROYECTO"
            etiqueta_proyecto = limpiar_texto(propiedad.find("div", {"class": "listing-card__project-label"}).text) if propiedad.find("div", {"class": "listing-card__project-label"}) else 'N/A'
            if etiqueta_proyecto == 'PROYECTO':
                continue  # Saltar propiedades que sean proyectos
            
            # Extraer precio y dejar solo los números
            precio = limpiar_texto(propiedad.find("div", {"class": "price"}).text) if propiedad.find("div", {"class": "price"}) else 'N/A'
            precio = extraer_numeros(precio)

            # Extraer ubicación
            ubicacion = limpiar_texto(propiedad.find("div", {"class": "listing-card__location"}).text) if propiedad.find("div", {"class": "listing-card__location"}) else 'N/A'

            # Extraer área y dejar solo los números
            area_div = propiedad.find("div", {"class": "card-icon__area"})
            area = limpiar_texto(area_div.find_next("span").text) if area_div and area_div.find_next("span") else 'N/A'
            area = extraer_numeros(area)

            # Extraer habitaciones y dejar solo los números
            habitaciones_span = propiedad.find("div", {"class": "card-icon__bedrooms"}).find_next("span", {"content": True})
            habitaciones = limpiar_texto(habitaciones_span.text) if habitaciones_span else 'N/A'
            habitaciones = extraer_numeros(habitaciones)

            # Extraer baños y dejar solo los números
            banos_span = propiedad.find("div", {"class": "card-icon__bathrooms"}).find_next("span", {"content": True})
            banos = limpiar_texto(banos_span.text) if banos_span else 'N/A'
            banos = extraer_numeros(banos)

            # Extraer agencia
            agencia = limpiar_texto(propiedad.find("div", {"class": "listing-card__agency-name"}).text) if propiedad.find("div", {"class": "listing-card__agency-name"}) else 'N/A'

            # Extraer fecha de publicación
            fecha_publicacion = limpiar_texto(propiedad.find("div", {"class": "listing-card__published-date"}).text) if propiedad.find("div", {"class": "listing-card__published-date"}) else 'N/A'

            # Escribir fila en el CSV (sin el campo de Título ni Etiqueta Proyecto)
            escritor_csv.writerow([precio, ubicacion, area, habitaciones, banos, agencia, fecha_publicacion])

    print(f"Datos procesados y guardados en {archivo_csv}")

# Función para encontrar y procesar todos los archivos txt que empiecen por "Properati_raw"
def procesar_archivos_txt_a_csv():
    carpeta_txt = 'data/output'
    carpeta_csv = 'data/csv'
    os.makedirs(carpeta_csv, exist_ok=True)

    for archivo in os.listdir(carpeta_txt):
        if archivo.startswith('Properati_raw') and archivo.endswith('.txt'):
            archivo_txt = os.path.join(carpeta_txt, archivo)
            nombre_csv = archivo.replace('Properati_raw', 'Properati').replace('.txt', '.csv')
            archivo_csv = os.path.join(carpeta_csv, nombre_csv)
            procesar_txt_a_csv(archivo_txt, archivo_csv)

# Uso de ejemplo
if __name__ == "__main__":
    procesar_archivos_txt_a_csv()
