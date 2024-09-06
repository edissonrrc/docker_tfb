import os
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime

def limpiar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

# Función para procesar el archivo de texto y extraer los datos
def procesar_txt_a_csv(archivo_txt, archivo_csv):
    with open(archivo_txt, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    soup = BeautifulSoup(contenido, 'html.parser')
    propiedades = soup.find_all("div", {"class": "listing-card__information"})
    
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        escritor_csv = csv.writer(csvfile, delimiter='|')
        # Escribir encabezado
        escritor_csv.writerow(['Título', 'Precio', 'Ubicación', 'Área', 'Habitaciones', 'Baños', 'Agencia', 'Fecha Publicación'])

        for propiedad in propiedades:
            titulo = limpiar_texto(propiedad.find("div", {"class": "listing-card__title"}).text) if propiedad.find("div", {"class": "listing-card__title"}) else 'N/A'
            precio = limpiar_texto(propiedad.find("div", {"class": "price"}).text) if propiedad.find("div", {"class": "price"}) else 'N/A'
            ubicacion = limpiar_texto(propiedad.find("div", {"class": "listing-card__location"}).text) if propiedad.find("div", {"class": "listing-card__location"}) else 'N/A'
            area = limpiar_texto(propiedad.find("div", {"class": "card-icon__area span"}).text) if propiedad.find("div", {"class": "card-icon__area span"}) else 'N/A'
            habitaciones = limpiar_texto(propiedad.find("span", {"content": True}).text) if propiedad.find("span", {"content": True}) else 'N/A'
            banos = limpiar_texto(propiedad.find("div", {"class": "card-icon__bathrooms"}).text) if propiedad.find("div", {"class": "card-icon__bathrooms"}) else 'N/A'
            agencia = limpiar_texto(propiedad.find("div", {"class": "listing-card__agency-name"}).text) if propiedad.find("div", {"class": "listing-card__agency-name"}) else 'N/A'
            fecha_publicacion = limpiar_texto(propiedad.find("div", {"class": "listing-card__published-date"}).text) if propiedad.find("div", {"class": "listing-card__published-date"}) else 'N/A'

            escritor_csv.writerow([titulo, precio, ubicacion, area, habitaciones, banos, agencia, fecha_publicacion])

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
