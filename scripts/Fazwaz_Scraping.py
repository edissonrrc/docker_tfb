import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Función para construir la URL basada en la ciudad y página
def construir_url(ciudad, pagina):
    base_url = f'https://www.fazwaz.com.ec/apartment-en-venta/ecuador/{ciudad}?mapEnable=0&order_by=verification_at|desc&page={pagina}'
    return base_url

# Función para procesar una página y guardar el HTML de las tarjetas en un archivo
def procesar_pagina(ciudad, pagina):
    url = construir_url(ciudad, pagina)
    try:
        # Realizar la solicitud con un timeout de 10 segundos
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx/5xx

        # Si la solicitud fue exitosa
        soup = BeautifulSoup(response.content, 'html.parser')
        propiedades = soup.findAll('div', class_='result-search__item')

        if propiedades:
            # Obtener la fecha y hora actual en formato ddmmaa_hhmm
            fecha_actual = datetime.now().strftime('%d%m%y_%H%M')

            # Definir la carpeta de salida
            carpeta_salida = '/opt/airflow/data/output'

            # Crear la carpeta si no existe
            os.makedirs(carpeta_salida, exist_ok=True)

            archivo_salida = f'{carpeta_salida}/Fazwaz_raw_p{pagina}_{fecha_actual}.txt'

            # Guardar las propiedades en un archivo
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

    except requests.exceptions.RequestException as e:
        # Manejar errores en la solicitud HTTP
        print(f"Error al acceder a la página {pagina}: {e}")

# Función principal para iterar sobre varias páginas
def extraer_html_propiedades(ciudad, paginas):
    for pagina in range(1, paginas + 1):
        procesar_pagina(ciudad, pagina)

# Uso de ejemplo
if __name__ == "__main__":
    ciudad = "pichincha/quito"
    num_paginas = 2
    extraer_html_propiedades(ciudad, num_paginas)
