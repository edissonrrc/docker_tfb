import os
import csv
import re
import spacy
from bs4 import BeautifulSoup

# Cargar el modelo en español de SpaCy
nlp = spacy.load("es_core_news_sm")

# Función para limpiar valores numéricos
def limpiar_numeros(texto):
    """Extrae números de un texto."""
    numeros = re.findall(r'\d+', texto)
    if len(numeros) == 1:
        return numeros[0]
    elif len(numeros) > 1:
        return ' - '.join(numeros)
    else:
        return "N/A"

# Función para procesar las descripciones con SpaCy y extraer habitaciones, baños, área
def extraer_informacion_spacy(descripcion):
    doc = nlp(descripcion)

    # Inicializar los valores como N/A
    habitaciones = "N/A"
    banos = "N/A"
    area = "N/A"
    
    # Buscar entidades relevantes
    for token in doc:
        if token.like_num:
            # Buscar el token previo y posterior para contexto
            prev_token = token.nbor(-1) if token.i > 0 else None
            next_token = token.nbor(1) if token.i < len(doc) - 1 else None

            # Si el número es seguido o precedido por "habitaciones", lo usamos como número de habitaciones
            if prev_token and prev_token.text.lower() in ["habitaciones", "habitación", "dormitorio", "dormitorios"]:
                habitaciones = token.text
            elif next_token and next_token.text.lower() in ["habitaciones", "habitación", "dormitorio", "dormitorios"]:
                habitaciones = token.text

            # Si el número es seguido o precedido por "baño" o "baños"
            if prev_token and prev_token.text.lower() in ["baños", "baño"]:
                banos = token.text
            elif next_token and next_token.text.lower() in ["baños", "baño"]:
                banos = token.text

            # Si el número es seguido o precedido por "m²"
            if next_token and next_token.text == "m²":
                area = token.text

    return habitaciones, banos, area

# Función para procesar archivos HTML
def procesar_archivos():
    carpeta_origen = 'data/html'
    carpeta_salida = 'data/csv'
    os.makedirs(carpeta_salida, exist_ok=True)

    archivos_html = [archivo for archivo in os.listdir(carpeta_origen) if archivo.startswith("Plusvalia") and archivo.endswith(".html")]

    for archivo_html in archivos_html:
        ruta_archivo = os.path.join(carpeta_origen, archivo_html)
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        precios = [limpiar_numeros(elem.get_text(strip=True)) for elem in soup.find_all('div', class_='Price-sc-12dh9kl-3')]
        ubicaciones = [elem.get_text(strip=True) for elem in soup.find_all('div', class_='LocationAddress-sc-ge2uzh-0')]
        ciudades = [elem.get_text(strip=True) for elem in soup.find_all('h2', class_='LocationLocation-sc-ge2uzh-2')]
        descripciones = [elem.get_text(" ", strip=True) for elem in soup.find_all('h3', class_='PostingDescription-sc-i1odl-11')]

        max_length = max(len(precios), len(ubicaciones), len(ciudades), len(descripciones))

        def completar_lista(lista, longitud, valor="N/A"):
            while len(lista) < longitud:
                lista.append(valor)
            return lista

        precios = completar_lista(precios, max_length)
        ubicaciones = completar_lista(ubicaciones, max_length)
        ciudades = completar_lista(ciudades, max_length)
        descripciones = completar_lista(descripciones, max_length)

        nombre_salida = archivo_html.replace("raw_", "").replace(".html", ".csv")
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)

        with open(ruta_salida, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Precio', 'Ubicación', 'Ciudad', 'Habitaciones', 'Baños', 'Área', 'Descripción'])

            for i in range(max_length):
                # Extraer información de habitaciones, baños y área usando SpaCy
                habitaciones, banos, area = extraer_informacion_spacy(descripciones[i])

                fila = [
                    precios[i],
                    ubicaciones[i],
                    ciudades[i],
                    habitaciones,
                    banos,
                    area,
                    descripciones[i].replace("\n", " ")
                ]

                writer.writerow(fila)

        print(f"Extracción completada y guardada en '{ruta_salida}'.")

if __name__ == "__main__":
    procesar_archivos()
