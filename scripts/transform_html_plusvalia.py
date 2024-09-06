from bs4 import BeautifulSoup
import csv
import os

# Lista de archivos HTML a procesar
archivos_html = [
    '/home/edisson/Descargas/Edisson_Reyes_TFB_Real_Estate_Market/html/plusvp2.html',  # Asegúrate de que la ruta sea correcta
    # Añadir más archivos si es necesario
]

# Función para procesar cada archivo HTML
def procesar_archivos(archivos):
    precios = []
    ubicaciones = []
    habitaciones = []
    banos = []
    areas = []
    precios_m2 = []
    fechas_publicacion = []
    descripciones = []

    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"El archivo {archivo} no existe.")
            continue

        with open(archivo, 'r', encoding='utf-8') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extracción de datos
        precios.extend([elem.get_text(strip=True) for elem in soup.find_all('div', class_='Price-sc-12dh9kl-3')])
        ubicaciones.extend([elem.get_text(strip=True) for elem in soup.find_all('div', class_='LocationAddress-sc-ge2uzh-0')])
        habitaciones.extend([elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "hab." in text if text else False)])
        banos.extend([elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "baño" in text.lower() if text else False)])
        areas.extend([elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "m²" in text if text else False)])
        precios_m2.extend([elem.get_text(strip=True) for elem in soup.find_all('span', string=lambda text: "/m²" in text if text else False)])
        fechas_publicacion.extend([elem.get_text(strip=True) for elem in soup.find_all('span', class_='PublicationDate-class')])  # Reemplaza con la clase correcta si se encuentra
        descripciones.extend([elem.get_text(" ", strip=True) for elem in soup.find_all('h3', class_='PostingDescription-sc-i1odl-11')])

    # Normalizar las listas para que tengan la misma longitud
    max_length = max(len(precios), len(ubicaciones), len(habitaciones), len(banos), len(areas), len(precios_m2), len(fechas_publicacion), len(descripciones))

    def completar_lista(lista, longitud, valor="N/A"):
        while len(lista) < longitud:
            lista.append(valor)
        return lista

    precios = completar_lista(precios, max_length)
    ubicaciones = completar_lista(ubicaciones, max_length)
    habitaciones = completar_lista(habitaciones, max_length)
    banos = completar_lista(banos, max_length)
    areas = completar_lista(areas, max_length)
    precios_m2 = completar_lista(precios_m2, max_length)
    fechas_publicacion = completar_lista(fechas_publicacion, max_length)
    descripciones = completar_lista(descripciones, max_length)

    # Guardar los datos en un archivo CSV
    output_dir = '/home/edisson/Descargas/Edisson_Reyes_TFB_Real_Estate_Market/data/'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'plusvalia_quito.csv')

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Precio', 'Ubicación', 'Habitaciones', 'Baños', 'Área', 'Precio/m²', 'Fecha de Publicación', 'Descripción'])

        for i in range(max_length):
            writer.writerow([
                precios[i],
                ubicaciones[i],
                habitaciones[i],
                banos[i],
                areas[i],
                precios_m2[i],
                fechas_publicacion[i],
                descripciones[i].replace("\n", " ")  # Reemplaza nuevas líneas dentro de la descripción por un espacio
            ])

    print(f"Extracción completada y guardada en '{output_file}'.")

# Ejecutar el procesamiento
procesar_archivos(archivos_html)
