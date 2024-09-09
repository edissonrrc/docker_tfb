import os
import pandas as pd
from datetime import datetime

# Función para cargar los datos de una inmobiliaria específica y extraer la fecha de captura
def cargar_datos_inmobiliaria(inmobiliaria, carpeta='data/csv'):
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith(inmobiliaria) and archivo.endswith('.csv')]
    
    if len(archivos_csv) == 0:
        raise ValueError(f"No se encontraron archivos CSV que comiencen con '{inmobiliaria}'. Verifica la ruta y los archivos.")
    
    # Procesar cada archivo CSV
    datos = pd.DataFrame()
    for archivo in archivos_csv:
        # Extraer la fecha del nombre del archivo, asumiendo el formato _ddmmaa_ dentro del nombre
        fecha_str = archivo.split('_')[2]
        fecha_captura = datetime.strptime(fecha_str, "%d%m%y").strftime('%Y-%m-%d')
        
        # Cargar los datos del CSV
        df = pd.read_csv(archivo, delimiter='|')
        # Agregar la columna "captura" con la fecha
        df['captura'] = fecha_captura
        
        # Concatenar con otros archivos CSV
        datos = pd.concat([datos, df], ignore_index=True)
    
    return datos

# Función para obtener una columna con un valor predeterminado si no existe
def obtener_columna(df, columna, valor_predeterminado='N/A'):
    if columna in df.columns:
        return df[columna]
    else:
        return pd.Series([valor_predeterminado] * len(df))

# Función para obtener la columna "agencia", si no existe, usar el nombre de la inmobiliaria
def obtener_agencia(df, columna, inmobiliaria):
    if columna in df.columns and not df[columna].isnull().all():
        return df[columna]
    else:
        return pd.Series([inmobiliaria] * len(df))

# Función para combinar columnas y convertirlas en string antes de hacer la concatenación
def combinar_columnas(df, columnas):
    # Convertir a cadena y combinar
    return df[columnas].fillna('').astype(str).agg(' '.join, axis=1).str.strip()

# Función para manejar la columna de estacionamientos, añadiendo el texto "Estacionamientos" al número
def manejar_estacionamientos(df, columna):
    if columna in df.columns:
        return df[columna].apply(lambda x: f"{int(x)} Estacionamientos" if pd.notnull(x) and x != '' else '')
    else:
        return pd.Series([''] * len(df))

# Función para procesar los datos de cada inmobiliaria y crear el DataFrame final con las columnas necesarias
def procesar_inmobiliaria(df, inmobiliaria):
    if inmobiliaria == 'Fazwaz':
        df_final = pd.DataFrame({
            'captura': df['captura'],  # Columna de captura añadida
            'precio': obtener_columna(df, 'Precio'),
            'agencia': obtener_agencia(df, 'Inmobiliaria', 'Fazwaz'),
            'aseos': obtener_columna(df, 'Baños'),
            'zona': obtener_columna(df, 'Ubicación'),
            'superficie': obtener_columna(df, 'Área'),
            'habitaciones': obtener_columna(df, 'Habitaciones'),
            'gastos': 'N/A',  # No hay información de gastos en Fazwaz
            'extras': combinar_columnas(df, ['Extras', 'Descripción Características', 'Descripción Título', 'Título'])
        })
    
    elif inmobiliaria == 'Mitula':
        df_final = pd.DataFrame({
            'captura': df['captura'],  # Columna de captura añadida
            'precio': obtener_columna(df, 'Precio'),
            'agencia': obtener_agencia(df, 'Nombre de la agencia', 'Mitula'),
            'aseos': obtener_columna(df, 'Baños'),
            'zona': obtener_columna(df, 'Ubicación'),
            'superficie': obtener_columna(df, 'Área (m²)'),
            'habitaciones': obtener_columna(df, 'Habitaciones'),
            'gastos': 'N/A',  # No hay información de gastos en Mitula
            'extras': combinar_columnas(df, ['Instalaciones', 'Título de la propiedad'])
        })
    
    elif inmobiliaria == 'Plusvalia':
        df_final = pd.DataFrame({
            'captura': df['captura'],  # Columna de captura añadida
            'precio': obtener_columna(df, 'Precio'),
            'agencia': obtener_agencia(df, 'Inmobiliaria', 'Plusvalia'),
            'aseos': obtener_columna(df, 'Baños'),
            'zona': combinar_columnas(df, ['Ciudad', 'Ubicación']),
            'superficie': obtener_columna(df, 'Área'),
            'habitaciones': obtener_columna(df, 'Habitaciones'),
            'gastos': obtener_columna(df, 'Expensas', 'N/A'),
            'extras': combinar_columnas(df, ['Características Principales', 'Descripción']) + ' ' + manejar_estacionamientos(df, 'Estacionamientos')
        })
    
    elif inmobiliaria == 'Properati':
        df_final = pd.DataFrame({
            'captura': df['captura'],  # Columna de captura añadida
            'precio': obtener_columna(df, 'Precio'),
            'agencia': obtener_agencia(df, 'Agencia', 'Properati'),
            'aseos': obtener_columna(df, 'Baños'),
            'zona': obtener_columna(df, 'Ubicación'),
            'superficie': obtener_columna(df, 'Área'),
            'habitaciones': obtener_columna(df, 'Habitaciones'),
            'gastos': 'N/A',  # No hay información de gastos en Properati
            'extras': 'N/A'  # No hay información de extras en Properati
        })
    
    elif inmobiliaria == 'Remax':
        df_final = pd.DataFrame({
            'captura': df['captura'],  # Columna de captura añadida
            'precio': obtener_columna(df, 'Precio'),
            'agencia': obtener_agencia(df, 'Inmobiliaria', 'Remax'),
            'aseos': obtener_columna(df, 'Baños'),
            'zona': obtener_columna(df, 'Dirección'),
            'superficie': obtener_columna(df, 'Superficie Cubierta (m²)'),
            'habitaciones': obtener_columna(df, 'Ambientes'),
            'gastos': obtener_columna(df, 'Expensas', 'N/A'),
            'extras': obtener_columna(df, 'Descripción', 'N/A')
        })
    
    return df_final

# Función para procesar todas las inmobiliarias y unificarlas en un solo DataFrame
def procesar_todas_inmobiliarias(carpeta='data/csv'):
    inmobiliarias = ['Fazwaz', 'Mitula', 'Plusvalia', 'Properati', 'Remax']
    datos_totales = pd.DataFrame()

    for inmobiliaria in inmobiliarias:
        # Cargar los datos de la inmobiliaria
        df = cargar_datos_inmobiliaria(inmobiliaria, carpeta)
        # Procesar y obtener el DataFrame final con las columnas requeridas
        df_preparado = procesar_inmobiliaria(df, inmobiliaria)
        # Concatenar los resultados en un único DataFrame
        datos_totales = pd.concat([datos_totales, df_preparado], ignore_index=True)
    
    return datos_totales

# Procesar todos los datos y guardarlos en un archivo CSV
df_final = procesar_todas_inmobiliarias()
#df_final.to_csv('data/csv/Transform1_propiedades.csv', index=False)

#print("Proceso completado. Archivo 'Transform1_propiedades.csv' generado.")

# Estandarización de los datos para mantener consistencia en tipos de datos

# Función para convertir precios a tipo numérico
def convertir_precio(precio):
    try:
        return float(str(precio).replace('$', '').replace(',', '').strip())
    except ValueError:
        return None

# Función para convertir área, habitaciones y aseos a numérico
def convertir_a_numerico(valor):
    try:
        return float(valor) if valor != '' else None
    except ValueError:
        return None

# Función para convertir fechas al formato YYYY-MM-DD
def convertir_fecha(fecha):
    try:
        return pd.to_datetime(fecha).strftime('%Y-%m-%d')
    except:
        return None

# Estandarizar las columnas precio, área, habitaciones, aseos y captura
df_final['precio'] = df_final['precio'].apply(convertir_precio)
df_final['superficie'] = df_final['superficie'].apply(convertir_a_numerico)
df_final['habitaciones'] = df_final['habitaciones'].apply(convertir_a_numerico)
df_final['aseos'] = df_final['aseos'].apply(convertir_a_numerico)
df_final['captura'] = df_final['captura'].apply(convertir_fecha)

# Visualizar las primeras filas tras la estandarización
print(df_final[['precio', 'superficie', 'habitaciones', 'aseos', 'captura']].head())

# Guardar el DataFrame estandarizado
df_final.to_csv('data/csv/Transform2_propiedades_std.csv', index=False)

print("Proceso completado. Archivo 'Transform2_propiedades_estandarizado.csv' generado.")
