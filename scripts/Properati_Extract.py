import os
import re
import csv
from bs4 import BeautifulSoup

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
        # Escribir encabezado con todos los campos extraíbles
        escritor_csv.writerow([
            'Título', 
            'Etiqueta Proyecto', 
            'Precio', 
            'Ubicación', 
            'Área', 
            'Habitaciones', 
            'Baños', 
            'Agencia', 
            'Fecha Publicación'
        ])

        for propiedad in propiedades:
            # Extraer título
            titulo = limpiar_texto(propiedad.find("div", {"class": "listing-card__title"}).text) if propiedad.find("div", {"class": "listing-card__title"}) else 'N/A'
            
            # Extraer etiqueta de proyecto
            etiqueta_proyecto = limpiar_texto(propiedad.find("div", {"class": "listing-card__project-label"}).text) if propiedad.find("div", {"class": "listing-card__project-label"}) else 'N/A'

            # Extraer precio
            precio = limpiar_texto(propiedad.find("div", {"class": "price"}).text) if propiedad.find("div", {"class": "price"}) else 'N/A'
            
            # Extraer ubicación
            ubicacion = limpiar_texto(propiedad.find("div", {"class": "listing-card__location"}).text) if propiedad.find("div", {"class": "listing-card__location"}) else 'N/A'
            
            # Extraer área (verificando que el span exista después del div)
            area_div = propiedad.find("div", {"class": "card-icon__area"})
            area = limpiar_texto(area_div.find_next("span").text) if area_div and area_div.find_next("span") else 'N/A'
            
            # Extraer habitaciones (verificando el span content)
            habitaciones_span = propiedad.find("div", {"class": "card-icon__bedrooms"}).find_next("span", {"content": True})
            habitaciones = limpiar_texto(habitaciones_span.text) if habitaciones_span else 'N/A'
            
            # Extraer baños (verificando el span content)
            banos_span = propiedad.find("div", {"class": "card-icon__bathrooms"}).find_next("span", {"content": True})
            banos = limpiar_texto(banos_span.text) if banos_span else 'N/A'
            
            # Extraer agencia
            agencia = limpiar_texto(propiedad.find("div", {"class": "listing-card__agency-name"}).text) if propiedad.find("div", {"class": "listing-card__agency-name"}) else 'N/A'
            
            # Extraer fecha de publicación
            fecha_publicacion = limpiar_texto(propiedad.find("div", {"class": "listing-card__published-date"}).text) if propiedad.find("div", {"class": "listing-card__published-date"}) else 'N/A'

            # Escribir fila en el CSV
            escritor_csv.writerow([titulo, etiqueta_proyecto, precio, ubicacion, area, habitaciones, banos, agencia, fecha_publicacion])

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
