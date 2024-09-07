import os
import csv
from bs4 import BeautifulSoup
import re

# Función para limpiar el texto y eliminar espacios innecesarios
def limpiar_texto(texto):
    return ' '.join(texto.split())

# Función para limpiar números, eliminando símbolos no deseados
def limpiar_numeros(texto):
    # Eliminamos cualquier símbolo que no sea un número
    return re.sub(r'[^0-9]', '', texto).strip()

# Función para buscar los archivos que empiezan con "Remax"
def buscar_archivos_txt(carpeta):
    archivos_txt = [f for f in os.listdir(carpeta) if f.startswith('Remax') and f.endswith('.txt')]
    return archivos_txt

# Función para procesar los archivos y convertirlos a CSV
def procesar_archivo_txt_a_csv(archivo_txt, carpeta_txt, carpeta_csv):
    with open(os.path.join(carpeta_txt, archivo_txt), 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Usar BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(contenido, 'html.parser')

    # Obtener todas las propiedades
    propiedades = soup.select('qr-card-property')

    # Obtener el nombre del archivo CSV de salida
    archivo_csv = os.path.join(carpeta_csv, archivo_txt.replace('raw_', '').replace('.txt', '.csv'))

    # Escribir en el archivo CSV
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        campos = ['Precio', 'Expensas', 'Dirección', 'Superficie Total (m²)', 'Superficie Cubierta (m²)', 
                  'Ambientes', 'Baños', 'Descripción', 'Agente', 'URL Propiedad']
        escritor_csv = csv.DictWriter(csvfile, fieldnames=campos, delimiter='|')
        
        escritor_csv.writeheader()
        
        # Extraer y escribir datos de cada propiedad
        for propiedad in propiedades:
            # Extraer precio y limpiar solo los números
            precio = limpiar_numeros(propiedad.select_one('.card__price').text) if propiedad.select_one('.card__price') else 'N/A'
            
            # Extraer expensas y limpiar solo los números dentro del rango válido
            expensas = int(re.findall(r'\d+', propiedad.select_one('.card__expenses').text)[0]) if propiedad.select_one('.card__expenses') and 0 <= int(re.findall(r'\d+', propiedad.select_one('.card__expenses').text)[0]) <= 10000 else 'N/A'

            # Extraer dirección
            direccion = limpiar_texto(propiedad.select_one('.card__address').text) if propiedad.select_one('.card__address') else 'N/A'
            
            # Extraer superficie total y convertir el formato numérico a europeo
            superficie_total = limpiar_numeros(propiedad.select_one('.feature--m2total span').text) if propiedad.select_one('.feature--m2total span') else 'N/A'
            
            # Extraer superficie cubierta y convertir el formato numérico a europeo
            superficie_cubierta = limpiar_numeros(propiedad.select_one('.feature--m2cover span').text) if propiedad.select_one('.feature--m2cover span') else 'N/A'

            # Extraer número de ambientes
            ambientes = limpiar_numeros(propiedad.select_one('.feature--ambientes span').text) if propiedad.select_one('.feature--ambientes span') else 'N/A'
            
            # Extraer número de baños
            banos = limpiar_numeros(propiedad.select_one('.feature--bathroom span').text) if propiedad.select_one('.feature--bathroom span') else 'N/A'
            
            # Extraer descripción
            descripcion = limpiar_texto(propiedad.select_one('.card__description').text) if propiedad.select_one('.card__description') else 'N/A'

            # Extraer nombre del agente
            agente = limpiar_texto(propiedad.select_one('.contact-person__info--name').text) if propiedad.select_one('.contact-person__info--name') else 'N/A'
            
            # Extraer URL de la propiedad
            url_propiedad = "https://www.remax.com.ec" + propiedad.select_one('a')['href'] if propiedad.select_one('a') else 'N/A'

            # Escribir la fila en el CSV
            escritor_csv.writerow({
                'Precio': precio,
                'Expensas': expensas,
                'Dirección': direccion,
                'Superficie Total (m²)': superficie_total,
                'Superficie Cubierta (m²)': superficie_cubierta,
                'Ambientes': ambientes,
                'Baños': banos,
                'Descripción': descripcion,
                'Agente': agente,
                'URL Propiedad': url_propiedad
            })

    print(f"Datos convertidos a CSV: {archivo_csv}")

# Función principal para convertir todos los archivos txt a CSV
def convertir_txt_a_csv():
    carpeta_txt = 'data/output'
    carpeta_csv = 'data/csv'
    
    # Crear carpeta CSV si no existe
    os.makedirs(carpeta_csv, exist_ok=True)
    
    # Buscar todos los archivos .txt en la carpeta de salida
    archivos_txt = buscar_archivos_txt(carpeta_txt)
    
    for archivo_txt in archivos_txt:
        procesar_archivo_txt_a_csv(archivo_txt, carpeta_txt, carpeta_csv)

# Uso de ejemplo
if __name__ == "__main__":
    convertir_txt_a_csv()
