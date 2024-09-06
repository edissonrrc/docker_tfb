import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Función para construir la URL basada en la ciudad y página
def construir_url(ciudad, pagina):
    base_url = f'https://www.properati.com.ec/s/{ciudad}/departamento/venta/{pagina}/'
    return base_url

# Función para procesar una página y guardar el HTML de las tarjetas en un archivo
def procesar_pagina(ciudad, pagina):
    url = construir_url(ciudad, pagina)
    response = requests.get(url)

    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        propiedades = soup.findAll("div", {"class": "listing-card__information"})

        if propiedades:
            # Obtener la fecha y hora actual en formato ddmmaa_hhmm
            fecha_actual = datetime.now().strftime('%d%m%y_%H%M')
            
            # Definir la carpeta de salida
            carpeta_salida = 'data/output'
            
            # Crear la carpeta si no existe
            os.makedirs(carpeta_salida, exist_ok=True)
            
            archivo_salida = f'{carpeta_salida}/Properati_raw_p{pagina}_{fecha_actual}.txt'
            
            with open(archivo_salida, 'w', encoding='utf-8') as archivo:
                archivo.write(f"Datos de la página {pagina} de {ciudad} obtenidos el {fecha_actual}:\n")
                archivo.write("=" * 80 + "\n")
                for idx, propiedad in enumerate(propiedades, 1):
                    archivo.write(f"Propiedad {idx}:\n")
                    archivo.write(propiedad.prettify() + "\n")
                    archivo.write("-" * 80 + "\n")
                    
            print(f"Datos guardados en {archivo_salida}")
        else:
            print(f"No se encontraron propiedades en la página {pagina}.")
    else:
        print(f"Error al acceder a la página {pagina}. Código de estado: {response.status_code}")

# Función principal para iterar sobre varias páginas
def extraer_html_propiedades(ciudad, paginas):
    for pagina in range(1, paginas + 1):
        procesar_pagina(ciudad, pagina)

# Uso de ejemplo
if __name__ == "__main__":
    ciudad = "quito"
    num_paginas = 2
    extraer_html_propiedades(ciudad, num_paginas)
