import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Función para construir la URL basada en la página de Mitula
def construir_url(pagina):
    base_url = 'https://casas.mitula.ec/casas/departamentos-quito?page={}'
    return base_url.format(pagina)

# Función para procesar una página y guardar el HTML de las tarjetas en un archivo
def procesar_pagina(pagina):
    url = construir_url(pagina)
    print(f"Accediendo a la URL: {url}")
    
    # Simular un navegador real mediante headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }
    
    response = requests.get(url, headers=headers)

    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        print(f"Página {pagina} descargada con éxito")
        soup = BeautifulSoup(response.content, 'html.parser')

        # Seleccionar tarjetas de propiedad en Mitula usando `soup.select()`
        tarjetas = soup.select('div.listing.listing-card')  # Selector más amplio para captar las propiedades

        if tarjetas:
            # Obtener la fecha y hora actual en formato ddmmaa_hhmm
            fecha_actual = datetime.now().strftime('%d%m%y_%H%M')

            # Definir la carpeta de salida
            carpeta_salida = 'data/output'
            os.makedirs(carpeta_salida, exist_ok=True)

            archivo_salida = f'{carpeta_salida}/Mitula_raw_p{pagina}_{fecha_actual}.txt'

            with open(archivo_salida, 'w', encoding='utf-8') as archivo:
                archivo.write(f"Datos de la página {pagina} obtenidos el {fecha_actual}:\n")
                archivo.write("=" * 80 + "\n")
                
                for idx, tarjeta in enumerate(tarjetas, 1):
                    # Escribir el HTML de la tarjeta en el archivo
                    archivo.write(f"Propiedad {idx}:\n")
                    archivo.write(tarjeta.prettify() + "\n")  # Escribir el HTML bien formateado
                    archivo.write("-" * 80 + "\n")
                    
            print(f"Datos guardados en {archivo_salida}")
        else:
            print(f"No se encontraron propiedades en la página {pagina}.")
    else:
        print(f"Error al acceder a la página {pagina}. Código de estado: {response.status_code}")

# Función principal para iterar sobre varias páginas
def extraer_html_propiedades(paginas):
    for pagina in range(1, paginas + 1):
        procesar_pagina(pagina)

# Uso de ejemplo
if __name__ == "__main__":
    num_paginas = 2  # Número de páginas a procesar
    extraer_html_propiedades(num_paginas)
