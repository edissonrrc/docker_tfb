import csv
import requests
from bs4 import BeautifulSoup
import re
import os
import datetime

def extraer_datos_fazwaz(ciudad, num_paginas):
    base_url = 'https://www.fazwaz.com.ec/apartment-en-venta/ecuador/{ciudad}?mapEnable=0&order_by=verification_at|desc&page={pagina}'
    carpeta_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    
    # Crear el directorio si no existe, usando exist_ok=True
    os.makedirs(carpeta_datos, exist_ok=True)
    
    archivo_csv = os.path.join(carpeta_datos, f"fazwaz_{ciudad.split('/')[-1]}_{datetime.date.today()}.csv")

    with open(archivo_csv, 'w', newline='', encoding='utf-8') as file:
        # Usar '|' como delimitador en lugar de comas
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['id', 'fecha_captura', 'precio', 'ubicacion', 'habitaciones', 'banos', 'area', 'precio_m2', 'fecha_publicacion', 'extras', 'web', 'descripcion'])

        for pagina in range(1, num_paginas + 1):
            print(f"Procesando página {pagina}...")
            url = base_url.format(ciudad=ciudad, pagina=pagina)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            property_containers = soup.find_all('div', class_="result-search__item")

            if not property_containers:
                break

            for container in property_containers:
                precio_tag = container.find('div', class_="price-tag")
                if precio_tag:
                    precio = re.findall(r"[\d,.]+", precio_tag.get_text(strip=True).replace('€', '').strip())[0]
                    precio = precio.replace(',', '')
                else:
                    precio = "Precio no encontrado"

                ubicacion = container.find('div', class_="location-unit").get_text(strip=True) if container.find('div', class_="location-unit") else "Ubicación no encontrada"
                habitaciones = container.find('i', class_="i-bed icon-info-unit").find_next_sibling(text=True).strip() if container.find('i', class_="i-bed icon-info-unit") else "Número de habitaciones no encontrado"
                banos = container.find('i', class_="i-bath icon-info-unit").find_next_sibling(text=True).strip() if container.find('i', class_="i-bath icon-info-unit") else "Número de baños no encontrado"
                area_tag = container.find('span', class_="dynamic-tooltip area-tooltip")
                if area_tag:
                    area = re.findall(r"[\d,.]+", area_tag.get_text(strip=True).replace('m²', '').strip())[0]
                    area = area.replace(',', '')
                else:
                    area = "Área no encontrada"

                precio_m2_tag = container.find('span', class_="dynamic-tooltip area-tooltip area-per-tooltip")
                if precio_m2_tag:
                    precio_m2 = re.findall(r"[\d,.]+", precio_m2_tag.get_text(strip=True).replace('€', '').strip())[0]
                    precio_m2 = precio_m2.replace(',', '')
                else:
                    precio_m2 = "Precio por m² no encontrado"
                
                fecha_publicacion = container.find('i', class_="manage-tag__icon last-updated-message").find_next_sibling(text=True).strip() if container.find('i', class_="manage-tag__icon last-updated-message") else "Fecha de publicación no encontrada"
                descripcion = container.find('div', class_="unit-info__shot-description").get_text(strip=True) if container.find('div', class_="unit-info__shot-description") else "Descripción no encontrada"

                fecha_captura = datetime.date.today()
                writer.writerow([hash((descripcion, ubicacion)), fecha_captura, precio, ubicacion, habitaciones, banos, area, precio_m2, fecha_publicacion, '', 'Fazwaz', descripcion])

    print(f"Extracción completada. El archivo CSV '{archivo_csv}' ha sido creado correctamente.")

# Uso de ejemplo
if __name__ == "__main__":
    ciudad = "pichincha/quito"
    num_paginas = 2
    extraer_datos_fazwaz(ciudad, num_paginas)

