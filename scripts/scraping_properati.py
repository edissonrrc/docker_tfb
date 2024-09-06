import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def extraer_datos_properati(ciudad, num_paginas):
    carpeta_datos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'output')
    
    # Crear el directorio si no existe, usando exist_ok=True
    os.makedirs(carpeta_datos, exist_ok=True)
    
    archivo_csv = os.path.join(carpeta_datos, f"properati_{ciudad}_{datetime.date.today()}.csv")
    
    with open(archivo_csv, "w", encoding="utf-8") as f:
        # Usar '|' como delimitador en lugar de comas
        encabezado = "id|fecha_captura|precio|precio_m2|area|habitaciones|banos|ubicacion|fecha_publicacion|extras|web|descripcion\n"
        f.write(encabezado)

        for num_pagina in range(1, num_paginas + 1):
            print(f"Procesando página {num_pagina}...")
            url_pagina = f'https://www.properati.com.ec/s/{ciudad}/departamento/venta/{num_pagina}/'
            
            try:
                respuesta = requests.get(url_pagina)
                respuesta.raise_for_status()
            except requests.HTTPError as err:
                print(f"Error HTTP al intentar acceder a {url_pagina}: {err}")
                continue
            except requests.RequestException:
                print(f"Error de conexión: El servidor está caído o la URL {url_pagina} es incorrecta")
                continue
            else:
                soup = BeautifulSoup(respuesta.text, 'html.parser')
                propiedades = soup.findAll("div", {"class": "listing-card__information"})

                for propiedad in propiedades:
                    descripcion = propiedad.find("div", {"class": "listing-card__title"}).get_text(strip=True)
                    precio_tag = propiedad.find("div", {"class": "price"})
                    if precio_tag:
                        precio_text = precio_tag.get_text(strip=True)
                        precio_match = re.findall(r"[\d,]+", precio_text)
                        if precio_match:
                            precio = precio_match[0].replace(",", "")
                        else:
                            precio = "No disponible"
                    else:
                        precio = "No disponible"

                    ubicacion = propiedad.find("div", {"class": "listing-card__location"}).get_text(strip=True)
                    habitaciones_tag = propiedad.find("div", {"class": "card-icon__bedrooms"})
                    if habitaciones_tag:
                        habitaciones = habitaciones_tag.find_next_sibling("span").get_text(strip=True)
                        habitaciones = re.findall(r"[\d]+", habitaciones)[0]
                    else:
                        habitaciones = "No disponible"

                    banos_tag = propiedad.find("div", {"class": "card-icon__bathrooms"})
                    if banos_tag:
                        banos = banos_tag.find_next_sibling("span").get_text(strip=True)
                        banos = re.findall(r"[\d]+", banos)[0]
                    else:
                        banos = "No disponible"

                    area_tag = propiedad.find("div", {"class": "card-icon__area"})
                    if area_tag:
                        area_text = area_tag.find_next_sibling("span").get_text(strip=True)
                        area_match = re.findall(r"[\d,]+", area_text)
                        if area_match:
                            area = area_match[0].replace(",", "")
                        else:
                            area = "No disponible"
                    else:
                        area = "No disponible"

                    try:
                        if precio != "No disponible" and area != "No disponible":
                            precio_m2 = round(float(precio) / float(area), 2)
                        else:
                            precio_m2 = "No disponible"
                    except ValueError:
                        precio_m2 = "No disponible"

                    fecha_publicacion = propiedad.find("div", {"class": "listing-card__published-date"}).get_text(strip=True)
                    fecha_captura = datetime.date.today()
                    # Usar '|' como delimitador en la línea de datos
                    linea = f'{hash((descripcion, ubicacion))}|{fecha_captura}|{precio}|{precio_m2}|{area}|{habitaciones}|{banos}|{ubicacion}|{fecha_publicacion}||Properati|{descripcion}\n'
                    f.write(linea)

    print(f"Datos guardados en {archivo_csv}")

# Uso de ejemplo
if __name__ == "__main__":
    ciudad = "quito"
    num_paginas = 2
    extraer_datos_properati(ciudad, num_paginas)

