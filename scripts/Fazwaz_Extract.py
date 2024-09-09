import os
import csv
from bs4 import BeautifulSoup
import re

# Función para limpiar el texto extraído
def limpiar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

# Función para limpiar los valores numéricos de símbolos ($, comas, etc.)
def limpiar_valor_numerico(valor):
    if valor:
        return re.sub(r'[^\d.]', '', valor)  # Elimina todo excepto dígitos y puntos
    return 'N/A'

# Función para procesar cada archivo TXT y extraer datos
def extraer_datos_fazwaz_html(archivo_txt, carpeta_csv):
    # Crear la carpeta de salida si no existe
    os.makedirs(carpeta_csv, exist_ok=True)
    
    archivo_nombre = os.path.basename(archivo_txt).replace('raw_', '').replace('.txt', '.csv')
    archivo_csv = os.path.join(carpeta_csv, archivo_nombre)
    
    with open(archivo_txt, 'r', encoding='utf-8') as f:
        contenido_html = f.read()

    soup = BeautifulSoup(contenido_html, 'html.parser')
    propiedades = soup.find_all('div', class_='result-search__item')

    # Definir los campos a extraer (sin incluir imágenes)
    campos = [
        'Precio', 'Título', 'Ubicación', 'Precio por m²', 'Área', 
        'Habitaciones', 'Baños', 'Descripción Características', 'Descripción Título', 
        'Última Actualización', 'Tipo de Propiedad', 'Enlace de Propiedad', 'Extras'
    ]
    
    # Abrir archivo CSV para escribir los datos
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as archivo_salida:
        writer = csv.writer(archivo_salida, delimiter='|')
        writer.writerow(campos)

        # Iterar sobre cada propiedad
        for propiedad in propiedades:
            # Extraer datos de la propiedad
            try:
                # Extraer solo el precio del div sin el contenido del span
                price_tag = propiedad.find('div', class_='price-tag')
                if price_tag:
                    precio = limpiar_valor_numerico(price_tag.contents[0])  # Extraer solo el contenido principal y limpiar
                else:
                    precio = 'N/A'

                # Título de la descripción
                descripcion_titulo_tag = propiedad.find('a', class_='unit-info__description-title')
                descripcion_titulo = limpiar_texto(descripcion_titulo_tag.string) if descripcion_titulo_tag else 'N/A'

                # Resto de los datos
                ubicacion = limpiar_texto(propiedad.find('div', class_='location-unit').string) if propiedad.find('div', class_='location-unit') else 'N/A'
                
                # Limpiar y extraer el Precio por m² (sin paréntesis ni símbolos)
                precio_m2_tag = propiedad.find('span', class_='area-per-tooltip')
                if precio_m2_tag:
                    precio_m2 = limpiar_valor_numerico(precio_m2_tag.string)  # Elimina paréntesis y símbolos
                else:
                    precio_m2 = 'N/A'
                
                # Extraer área desde el span con data-tooltip="Superficie habitable" y limpiar
                area_tag = propiedad.find('span', class_='dynamic-tooltip', attrs={'data-tooltip': 'Superficie habitable'})
                if area_tag:
                    area = limpiar_valor_numerico(area_tag.string)  # Elimina "m²"
                else:
                    area = 'N/A'

                habitaciones = limpiar_texto(propiedad.find('i', class_='i-bed').find_next_sibling(string=True)) if propiedad.find('i', class_='i-bed') else 'N/A'
                banos = limpiar_texto(propiedad.find('i', class_='i-bath').find_next_sibling(string=True)) if propiedad.find('i', class_='i-bath') else 'N/A'

                # Descripción de características
                descripcion_caracteristicas = limpiar_texto(propiedad.find('div', class_='unit-info__shot-description').string) if propiedad.find('div', class_='unit-info__shot-description') else 'N/A'

                # Última actualización
                actualizacion = limpiar_texto(propiedad.find('i', class_='manage-tag__icon').find_next_sibling(string=True)) if propiedad.find('i', class_='manage-tag__icon') else 'N/A'

                tipo_propiedad = limpiar_texto(propiedad.find('i', class_='i-9').find_next_sibling(string=True)) if propiedad.find('i', class_='i-9') else 'N/A'
                enlace = propiedad.find('a', class_='link-unit')['href'] if propiedad.find('a', class_='link-unit') else 'N/A'

                # Extraer "Extras" incluyendo tanto los `unit-info__basic-info` como `unit-info__feature`
                extras_basicos = [limpiar_texto(extra.string) for extra in propiedad.find_all('div', class_='unit-info__basic-info')]
                extras_caracteristicas = [limpiar_texto(extra.string) for extra in propiedad.find_all('div', class_='unit-info__feature')]
                
                # Unir ambas listas de extras
                extras = ', '.join(extras_basicos + extras_caracteristicas) if (extras_basicos or extras_caracteristicas) else 'N/A'

                # Escribir fila en el CSV (sin la columna de imágenes)
                writer.writerow([precio, descripcion_titulo, ubicacion, precio_m2, area, habitaciones, banos, 
                                descripcion_caracteristicas, descripcion_titulo, actualizacion, tipo_propiedad, enlace, extras])
            except Exception as e:
                print(f"Error procesando una propiedad: {e}")
                continue

    print(f"Extracción completada. Datos guardados en {archivo_csv}")

# Función para buscar archivos y procesarlos
def procesar_archivos_fazwaz(carpeta_origen, carpeta_salida):
    # Buscar archivos que empiezan con 'Fazwaz_raw' en la carpeta de origen
    for archivo in os.listdir(carpeta_origen):
        if archivo.startswith('Fazwaz_raw') and archivo.endswith('.txt'):
            archivo_txt = os.path.join(carpeta_origen, archivo)
            extraer_datos_fazwaz_html(archivo_txt, carpeta_salida)

if __name__ == "__main__":
    carpeta_origen = 'data/output'
    carpeta_salida = 'data/csv'
    procesar_archivos_fazwaz(carpeta_origen, carpeta_salida)
