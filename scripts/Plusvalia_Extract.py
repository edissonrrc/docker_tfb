import os
import csv
import re
from bs4 import BeautifulSoup

# Función para limpiar los valores
def limpiar_numeros(texto):
    """Deja solo los números en el texto."""
    numeros = re.findall(r'\d+', texto)
    if len(numeros) == 1:
        return numeros[0]
    elif len(numeros) > 1:
        return ' - '.join(numeros)
    else:
        return "N/A"

# Función para limpiar el precio
def limpiar_precio(precio):
    return re.sub(r'[^\d]', '', precio)

# Función para verificar si una fila tiene más valores faltantes
def demasiados_valores_faltantes(fila, limite_faltantes=6):
    # Contar cuántos valores "N/A" hay en la fila
    valores_faltantes = fila.count("N/A")
    return valores_faltantes > limite_faltantes

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
        precios = [limpiar_precio(elem.get_text(strip=True)) for elem in soup.find_all('div', class_='Price-sc-12dh9kl-3')]
        ubicaciones = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='LocationAddress-sc-ge2uzh-0')]
        ciudades = [elem.get_text(strip=True) for elem in soup.find_all('h2', class_='LocationLocation-sc-ge2uzh-2')]
        expensas = [limpiar_numeros(elem.get_text(strip=True)) for elem in soup.find_all('div', class_='Expenses-sc-12dh9kl-1')]
        habitaciones = [limpiar_numeros(elem.get_text(strip=True)) for elem in soup.find_all('span', string=lambda text: "hab." in text if text else False)]
        banos = [limpiar_numeros(elem.get_text(strip=True)) for elem in soup.find_all('span', string=lambda text: "baño" in text.lower() if text else False)]
        areas = [limpiar_numeros(elem.get_text(strip=True)) for elem in soup.find_all('span', string=lambda text: "m²" in text if text else False)]
        estacionamientos = [limpiar_numeros(elem.get_text(strip=True)) for elem in soup.find_all('span', string=lambda text: "estac" in text if text else False)]
        descripciones = [elem.get_text(" ", strip=True) for elem in soup.find_all('h3', class_='PostingDescription-sc-i1odl-11')]
        destacados = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='HighLight-sc-i1odl-10')]

        # Extraer características principales
        caracteristicas_principales = [
            elem.get_text(" ", strip=True) 
            for elem in soup.find_all('h3', class_='PostingMainFeaturesBlock-sc-1uhtbxc-0')
        ]

        # Extraer enlace a la página completa
        enlaces = [
            elem['href'] for elem in soup.find_all('a', href=True) 
            if 'propiedades' in elem['href']
        ]

        # Normalizar la longitud de las listas
        max_length = max(len(precios), len(ubicaciones), len(ciudades), len(expensas), len(habitaciones), len(banos), len(areas), len(estacionamientos), len(descripciones), len(destacados), len(caracteristicas_principales), len(enlaces))

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
        descripciones = completar_lista(descripciones, max_length)
        destacados = completar_lista(destacados, max_length)
        caracteristicas_principales = completar_lista(caracteristicas_principales, max_length)
        enlaces = completar_lista(enlaces, max_length)

        # Extraer la fecha y hora del nombre del archivo HTML
        nombre_salida = archivo_html.replace("raw_", "").replace(".html", ".csv")
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)

        # Guardar los datos en un archivo CSV con separadores tipo "|"
        with open(ruta_salida, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Precio', 'Ubicación', 'Ciudad', 'Expensas', 'Habitaciones', 'Baños', 'Área', 'Estacionamientos', 'Descripción', 'Destacado', 'Características Principales', 'Enlace'])

            for i in range(max_length):
                fila = [
                    precios[i],
                    ubicaciones[i],
                    ciudades[i],
                    expensas[i],
                    habitaciones[i],
                    banos[i],
                    areas[i],
                    estacionamientos[i],
                    descripciones[i].replace("\n", " "),
                    destacados[i],
                    caracteristicas_principales[i],
                    enlaces[i]
                ]
                
                # Solo escribir la fila si no tiene más de x valores faltantes
                if not demasiados_valores_faltantes(fila, limite_faltantes=6):
                    writer.writerow(fila)

        print(f"Extracción completada y guardada en '{ruta_salida}'.")

# Ejecutar la función
if __name__ == "__main__":
    procesar_archivos()
