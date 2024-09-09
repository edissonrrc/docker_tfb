import pandas as pd
import spacy
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# Cargar el CSV con datos estandarizados
df = pd.read_csv('data/csv/Transform2_propiedades_std.csv')

# Inicializar el modelo de spaCy para español
nlp = spacy.load('es_core_news_md')

# 1. Estudio Profundo de la Columna "extras" usando NLP

# Definir una lista más extensa de palabras clave comunes en el sector inmobiliario para identificar "extras"
palabras_clave_extras = [
    'piscina', 'gimnasio', 'terraza', 'balcón', 'jardín', 'ascensor', 'vista', 'patio', 'estacionamiento', 
    'parqueadero', 'parqueo', 'jacuzzi', 'mascotas', 'amueblado', 'sauna', 'seguridad', 'áreas verdes', 
    'chalet', 'parque', 'guardería', 'playa', 'garaje', 'vigilante', 'barbacoa', 'trastero', 
    'lavadero', 'calefacción', 'aire acondicionado', 'sótano', 'zotehuela', 'portería', 'sala de juegos', 
    'salón de eventos', 'club', 'zona infantil', 'zona de estudio', 'solarium', 'spa', 'biblioteca', 
    'despacho', 'cámaras de seguridad', 'zona BBQ', 'cancha de tenis', 'cancha de paddle', 'luz natural', 
    'zona comercial', 'parque privado', 'zona escolar', 'cerca del metro', 'vigilancia privada', 'zona peatonal',
    'domótica', 'cine', 'vigilancia 24 horas', 'piscina climatizada', 'terraza privada', 'gym privado', 
    'roof garden', 'zona de coworking', 'paneles solares', 'electrodomésticos', 'circuito cerrado'
]

# Función para limpiar y procesar el texto en "extras" y extraer solo las palabras clave relevantes
def extraer_extras(texto):
    doc = nlp(texto)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    # Filtrar las palabras clave que representan extras reales
    extras_reales = [token for token in tokens if any(re.search(palabra, token, re.IGNORECASE) for palabra in palabras_clave_extras)]
    return ', '.join(extras_reales) if extras_reales else 'sin extra'

# Aplicar la función de limpieza y extracción de extras
df['extras'] = df['extras'].fillna('').apply(extraer_extras)

# 2. Completar valores faltantes en otras columnas usando la información de "extras"

# Función para completar valores faltantes de baños, habitaciones, etc. basados en la columna "extras"
def completar_valores_faltantes(row):
    texto_extras = row['extras']
    completados = {}
    # Buscar patrones en la columna "extras" para extraer valores de baños, habitaciones, etc.
    if pd.isna(row['habitaciones']):
        match_hab = re.search(r'(\d+)\s*(habitación|cuarto|dormitorio)', texto_extras)
        if match_hab:
            row['habitaciones'] = int(match_hab.group(1))
            completados['habitaciones'] = row['habitaciones']

    if pd.isna(row['aseos']):
        match_banos = re.search(r'(\d+)\s*(baño|aseo)', texto_extras)
        if match_banos:
            row['aseos'] = int(match_banos.group(1))
            completados['aseos'] = row['aseos']

    if pd.isna(row['superficie']):
        match_superficie = re.search(r'(\d+)\s*m2', texto_extras)
        if match_superficie:
            row['superficie'] = float(match_superficie.group(1))
            completados['superficie'] = row['superficie']
    
    if completados:
        print(f"Valores completados en la fila {row.name}: {completados}")
    
    return row

# Aplicar la función a cada fila del DataFrame para completar valores faltantes
df = df.apply(completar_valores_faltantes, axis=1)

# 3. Crear una nube de palabras para visualizar los "extras" más comunes
def crear_nube_palabras(texto):
    wordcloud = WordCloud(width=800, height=400, max_words=100).generate(texto)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# Concatenar todos los extras filtrados para generar la nube de palabras
todos_extras = ' '.join(df['extras'].fillna(''))
crear_nube_palabras(todos_extras)

# Guardar el DataFrame enriquecido y completado en un nuevo archivo CSV
df.to_csv('data/csv/Transform3_propiedades_nlp_enriquecido.csv', index=False)

print("Proceso de normalización y enriquecimiento completado. Archivo 'Transform3_propiedades_nlp_enriquecido.csv' generado.")
