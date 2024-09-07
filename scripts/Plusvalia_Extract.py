import os
import csv
import random
from bs4 import BeautifulSoup

# Función para procesar archivos HTML
def procesar_archivos():
    # Definir las carpetas de origen y salida
    carpeta_origen = 'data/html'
    carpeta_salida = 'data/csv'

    # Crear la carpeta de salida si no existe
    os.makedirs(carpeta_salida, exist_ok=True)

    # Obtener todos los archivos HTML que empiecen con "Plusvalia" en la carpeta de origen
    archivos_html = [archivo for archivo in os.listdir(carpeta_origen) if archivo.startswith("Plusvalia") and archivo.endswith(".html")]

    for archivo_html in archivos_html:
        ruta_archivo = os.path.join(carpeta_origen, archivo_html)

        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Usar BeautifulSoup para analizar el contenido del HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extracción de datos
        precios = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='Price-sc-12dh9kl-3')]
        ubicaciones = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='LocationAddress-sc-ge2uzh-0')]
        ciudades = [elem.get_text(strip=True) for elem in soup.find_all('h2', class_='LocationLocation-sc-ge2uzh-2')]
        expensas = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='Expenses-sc-12dh9kl-1')]
        habitaciones = [elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "hab." in text if text else False)]
        banos = [elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "baño" in text.lower() if text else False)]
        areas = [elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "m²" in text if text else False)]
        estacionamientos = [elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "estac" in text if text else False)]
        precios_m2 = [elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "/m²" in text if text else False)]
        fechas_publicacion = [elem.get_text(strip=True) for elem in soup.find_all('span', class_='PublicationDate-class')]  # Reemplaza con la clase correcta si se encuentra
        descripciones = [elem.get_text(" ", strip=True) for elem in soup.find_all('h3', class_='PostingDescription-sc-i1odl-11')]
        logos_agencias = [elem['src'] for elem in soup.find_all('img', {'data-qa': 'POSTING_CARD_PUBLISHER'})]
        destacados = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='HighLight-sc-i1odl-10')]

        # Normalizar la longitud de las listas
        max_length = max(len(precios), len(ubicaciones), len(ciudades), len(expensas), len(habitaciones), len(banos), len(areas), len(estacionamientos), len(precios_m2), len(fechas_publicacion), len(descripciones), len(logos_agencias), len(destacados))

        def completar_lista(lista, longitud, valor="N/A"):
            while len(lista) < longitud:
                lista.append(valor)
            return lista

        precios = completar_lista(precios, max_length)
        ubicaciones = completar_lista(ubicaciones, max_length)
        ciudades = completar_lista(ciudades, max_length)
        expensas = completar_lista(expensas, max_length)
        habitaciones = completar_lista(habitaciones, max_length)
        banos = completar_lista(banos, max_length)
        areas = completar_lista(areas, max_length)
        estacionamientos = completar_lista(estacionamientos, max_length)
        precios_m2 = completar_lista(precios_m2, max_length)
        fechas_publicacion = completar_lista(fechas_publicacion, max_length)
        descripciones = completar_lista(descripciones, max_length)
        logos_agencias = completar_lista(logos_agencias, max_length)
        destacados = completar_lista(destacados, max_length)

        # Extraer la fecha y hora del nombre del archivo HTML
        nombre_salida = archivo_html.replace("raw_", "").replace(".html", ".csv")
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)

        # Guardar los datos en un archivo CSV
        with open(ruta_salida, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Precio', 'Ubicación', 'Ciudad', 'Expensas', 'Habitaciones', 'Baños', 'Área', 'Estacionamientos', 'Precio/m²', 'Fecha de Publicación', 'Descripción', 'Logo Agencia', 'Destacado'])

            for i in range(max_length):
                writer.writerow([
                    precios[i],
                    ubicaciones[i],
                    ciudades[i],
                    expensas[i],
                    habitaciones[i],
                    banos[i],
                    areas[i],
                    estacionamientos[i],
                    precios_m2[i],
                    fechas_publicacion[i],
                    descripciones[i].replace("\n", " "),
                    logos_agencias[i],
                    destacados[i]
                ])

        print(f"Extracción completada y guardada en '{ruta_salida}'.")

# Ejecutar la función
if __name__ == "__main__":
    procesar_archivos()
