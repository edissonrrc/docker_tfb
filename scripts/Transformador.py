import os
from datetime import datetime
import spacy
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import r2_score, mean_squared_error
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

########################### FASE 1: CARGAR Y PROCESAR DATOS ###########################

# Función para cargar los datos de una inmobiliaria específica y extraer la fecha de captura
def cargar_datos_inmobiliaria(inmobiliaria, carpeta='/opt/airflow/data/csv'):
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith(inmobiliaria) and archivo.endswith('.csv')]
    
    if len(archivos_csv) == 0:
        raise ValueError(f"No se encontraron archivos CSV que comiencen con '{inmobiliaria}'. Verifica la ruta y los archivos.")
    
    # Procesar cada archivo CSV y concatenar en un DataFrame
    datos = pd.DataFrame()
    for archivo in archivos_csv:
        fecha_str = archivo.split('_')[2]
        fecha_captura = datetime.strptime(fecha_str, "%d%m%y").strftime('%Y-%m-%d')
        df = pd.read_csv(archivo, delimiter='|')
        df['captura'] = fecha_captura
        datos = pd.concat([datos, df], ignore_index=True)
    
    return datos

# Función para obtener una columna, si no existe la llena con NaN
def obtener_columna(df, columna):
    return df[columna] if columna in df.columns else pd.Series([None] * len(df))

# Función para obtener la columna "agencia", si no existe, usar el nombre de la inmobiliaria
def obtener_agencia(df, columna, inmobiliaria):
    if columna in df.columns and not df[columna].isnull().all():
        return df[columna]
    return pd.Series([inmobiliaria] * len(df))

# Función para combinar columnas y convertirlas a string
def combinar_columnas(df, columnas):
    columnas_existentes = [col for col in columnas if col in df.columns]
    if columnas_existentes:
        return df[columnas_existentes].fillna('').astype(str).agg(' '.join, axis=1).str.strip()
    return pd.Series([''] * len(df))

# Función para manejar la columna de estacionamientos y agregar el texto "Estacionamientos"
def manejar_estacionamientos(df, columna):
    if columna in df.columns:
        return df[columna].apply(lambda x: f"{int(x)} Estacionamientos" if pd.notnull(x) and x != '' else '')
    return pd.Series([''] * len(df))

# Función para procesar los datos de cada inmobiliaria y crear el DataFrame final con las columnas necesarias
def procesar_inmobiliaria(df, inmobiliaria):
    mappings = {
        'Fazwaz': {
            'agencia': 'Inmobiliaria', 'zona': 'Ubicación', 'superficie': 'Área',
            'habitaciones': 'Habitaciones', 'gastos': 'Expensas', 'extras': ['Extras', 'Descripción Características', 'Descripción Título', 'Título']
        },
        'Mitula': {
            'agencia': 'Nombre de la agencia', 'zona': 'Ubicación', 'superficie': 'Área (m²)',
            'habitaciones': 'Habitaciones', 'gastos': 'Expensas', 'extras': ['Instalaciones', 'Título de la propiedad']
        },
        'Plusvalia': {
            'agencia': 'Inmobiliaria', 'zona': ['Ciudad', 'Ubicación'], 'superficie': 'Área',
            'habitaciones': 'Habitaciones', 'gastos': 'Expensas', 'extras': ['Características Principales', 'Descripción'], 'estacionamientos': 'Estacionamientos'
        },
        'Properati': {
            'agencia': 'Agencia', 'zona': 'Ubicación', 'superficie': 'Área',
            'habitaciones': 'Habitaciones', 'gastos': 'Expensas', 'extras': 'Descripción'
        },
        'Remax': {
            'agencia': 'Agencia', 'zona': 'Dirección', 'superficie': 'Superficie Cubierta (m²)',
            'habitaciones': 'Ambientes', 'gastos': 'Expensas', 'extras': 'Descripción'
        }
    }

    columns = mappings[inmobiliaria]
    df_final = pd.DataFrame({
        'captura': df['captura'],
        'precio': obtener_columna(df, 'Precio'),
        'agencia': obtener_agencia(df, columns['agencia'], inmobiliaria),
        'aseos': obtener_columna(df, 'Baños'),
        'zona': combinar_columnas(df, columns['zona']) if isinstance(columns['zona'], list) else obtener_columna(df, columns['zona']),
        'superficie': obtener_columna(df, columns['superficie']),
        'habitaciones': obtener_columna(df, columns['habitaciones']),
        'gastos': obtener_columna(df, columns['gastos']),
        'extras': combinar_columnas(df, columns['extras']) + (' ' + manejar_estacionamientos(df, columns.get('estacionamientos', '')) if 'estacionamientos' in columns else '')
    })
    
    return df_final

# Procesar todas las inmobiliarias y unificarlas en un solo DataFrame
def procesar_todas_inmobiliarias(carpeta='/opt/airflow/data/csv'):
    inmobiliarias = ['Fazwaz', 'Mitula', 'Properati', 'Remax'] # De momento se elimia Plusvalia
    datos_totales = pd.DataFrame()

    for inmobiliaria in inmobiliarias:
        df = cargar_datos_inmobiliaria(inmobiliaria, carpeta)
        df_preparado = procesar_inmobiliaria(df, inmobiliaria)
        datos_totales = pd.concat([datos_totales, df_preparado], ignore_index=True)
    
    return datos_totales

# Procesar todos los datos
df_final = procesar_todas_inmobiliarias()

print("FASE 1 DONE: CARGAR Y PROCESAR DATOS")


########################### FASE 2: ESTANDARIZACIÓN Y LIMPIEZA ###########################

# Función para convertir precios, habitaciones y gastos a enteros
def convertir_a_entero(valor):
    try:
        return int(float(valor)) if valor != '' else None
    except ValueError:
        return None

# Función para convertir área, aseos (Baños) a decimal
def convertir_a_float(valor):
    try:
        return float(valor) if valor != '' else None
    except ValueError:
        return None

# Función para convertir fechas al formato YYYY-MM-DD aunque es para comprobar solamente
def convertir_fecha(fecha):
    try:
        return pd.to_datetime(fecha).strftime('%Y-%m-%d')
    except:
        return None

# Estandarizar las columnas precio, habitaciones, gastos como enteros y aseos como float
df_final['precio'] = df_final['precio'].apply(convertir_a_entero)
df_final['habitaciones'] = df_final['habitaciones'].apply(convertir_a_entero)
df_final['gastos'] = df_final['gastos'].apply(convertir_a_entero)
df_final['aseos'] = df_final['aseos'].apply(convertir_a_float)
df_final['captura'] = df_final['captura'].apply(convertir_fecha)

# Guardar el DataFrame estandarizado
df_final.to_csv('data/csv/Transform1_std.csv', index=False)

# Análisis de valores nulos
#missing_values = df_final.isnull().sum()

print("FASE 2 DONE: ESTANDARIZACIÓN Y LIMPIEZA")


########################### FASE 3: NLP PARA COMPLETAR GAPS ###########################

# Inicializar spaCy con un modelo avanzado de español
nlp = spacy.load('es_core_news_md')

# Limpieza de la Columna "Zona"
def limpiar_zona(zona):
    if zona == "N/A":
        return "Quito"
    return re.sub(r'\b(de Quito|, Quito|, Pichincha|, Norte De Quito|, Valle Tumbaco| CUMBAYÁ| CUMBAYA|, Iñaquito|, Jipijapa| de| -|, Centro Norte|S/N|)\b', '', zona).strip()

df_final['zona'] = df_final['zona'].fillna("N/A").apply(limpiar_zona)

# Función para extraer información de habitaciones, baños, superficie y gastos desde 'extras'
def extraer_informacion_basica(texto):
    info = {
        "habitaciones": None,
        "baños": None,
        "superficie": None,
        "gastos": None
    }
    match_habitaciones = re.search(r'(\d+)\s*(?:a\s*(\d+)\s*)?(habitación|dormitorio|recámara|cuarto|hab|ambiente)', texto, re.IGNORECASE)
    match_banos = re.search(r'(\d+)\s*(?:a\s*(\d+)\s*)?(baño|aseo)', texto, re.IGNORECASE)
    match_superficie = re.search(r'(\d+)\s*(?:a\s*(\d+)\s*)?(m2|metros cuadrados|mt2|m²)', texto, re.IGNORECASE)
    match_gastos = re.search(r'alicuota\s*\$?(\d+)', texto, re.IGNORECASE)

    if match_habitaciones:
        info["habitaciones"] = int(match_habitaciones.group(2) or match_habitaciones.group(1))
    if match_banos:
        info["baños"] = float(match_banos.group(2) or match_banos.group(1))
    if match_superficie:
        info["superficie"] = float(match_superficie.group(2) or match_superficie.group(1))
    if match_gastos:
        info["gastos"] = float(match_gastos.group(1))
    return info

# Función para procesar "extras" y completar los valores faltantes
def procesar_extras_y_completar(row):
    texto_extras = str(row['extras']).lower()
    info_basica = extraer_informacion_basica(texto_extras)
    
    completados = {}
    if pd.isna(row['habitaciones']) and info_basica["habitaciones"]:
        row['habitaciones'] = info_basica["habitaciones"]
        completados['habitaciones'] = row['habitaciones']
    if pd.isna(row['aseos']) and info_basica["baños"]:
        row['aseos'] = info_basica["baños"]
        completados['aseos'] = row['aseos']
    if pd.isna(row['superficie']) and info_basica["superficie"]:
        row['superficie'] = info_basica["superficie"]
        completados['superficie'] = row['superficie']
    if pd.isna(row['gastos']) and info_basica["gastos"]:
        row['gastos'] = info_basica["gastos"]
        completados['gastos'] = row['gastos']
    
    if completados:
        print(f"Valores completados en la fila {row.name}: {completados}")

    return row

# Aplicar el procesamiento de extras y completar valores faltantes en todas las filas
df_final = df_final.apply(procesar_extras_y_completar, axis=1)

# Guardar el DataFrame en un nuevo CSV
#df_final.to_csv('data/csv/Transform1_enriquecido.csv', index=False)

print("FASE 3 DONE: NLP PARA COMPLETAR GAPS")


########################### FASE 4: LIMPIEZA COLUMNA EXTRAS ###########################

# Lista de extras valiosos
extras_valiosos = [
    'piscina', 'terraza', 'barbacoa', 'bbq', 'gimnasio', 
    'jacuzzi', 'spa', 'sauna', 'parqueadero', 'garaje', 
    'bodega', 'balcón', 'ascensor', 'zona de juegos', 
    'pista de correr', 'áreas verdes', 'circuito cerrado de cámaras',
    'chimenea', 'conserje', 'garita de guardianía', 'nuovo', 'pontebello',
    'acceso para personas con discapacidad', 'patio', 
    'vista panorámica', 'seguridad', 'cuarto de servicio', 
    'internet', 'alarma', 'calefacción', 'cancha de tenis', 'centrally'
    'completamente amoblado', 'zona bbq', 'sin amoblar', 'parking',
    'jardín', 'piscina privada', 'gimnasio privado', 'estacionamiento',
    'quiet', 'brand-new', 'views', 'center', 'privileged', 'condo', 
    'amenities', 'mountains', 'condos', 'appreciation', 'luxury', 'condado'
]

# Filtrar los extras que aportan valor
def filtrar_extras_valiosos(texto_extras, extras_valiosos):
    texto_extras = texto_extras.lower() 
    extras_filtrados = [extra for extra in extras_valiosos if extra in texto_extras]
    return ', '.join(extras_filtrados) if extras_filtrados else None

# Procesar y asignar "Sin Extras" en caso de que no haya extras valiosos
def procesar_extras_y_filtrar(row):
    texto_extras = str(row['extras']).lower()
    extras_valiosos_filtrados = filtrar_extras_valiosos(texto_extras, extras_valiosos)
    # Si no hay extras valiosos, asignar "Sin Extras"
    row['extras'] = extras_valiosos_filtrados if extras_valiosos_filtrados else "sin extras"
    return row

# Aplicar el procesamiento de extras para filtrar los que aportan valor
df_final = df_final.apply(procesar_extras_y_filtrar, axis=1)


print("FASE 4 DONE: LIMPIEZA COLUMNA EXTRAS")


########################### FASE 5: PREDICCIÓN DE COLUMNA GASTOS ###########################

# Definir las características predictoras y la variable objetivo
X_con_gastos = df_final[['superficie', 'habitaciones', 'aseos']].values
y_con_gastos = df_final['gastos'].values

# Filtrar los datos para eliminar las filas con NaN en y (gastos) para el entrenamiento
mask_entrenamiento = ~np.isnan(y_con_gastos) 
X_train = X_con_gastos[mask_entrenamiento]   
y_train = y_con_gastos[mask_entrenamiento]    

# Dividir los datos en conjunto de entrenamiento y prueba
X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Crear el modelo XGBoost
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)

# Entrenar el modelo solo con los datos que tienen valores de gastos
xgb_model.fit(X_train_split, y_train_split)

# Realizar predicciones en el conjunto de prueba
y_pred_split = xgb_model.predict(X_test_split)

# Predecir los valores faltantes de gastos (donde gastos es NaN)
mask_prediccion = np.isnan(y_con_gastos)
X_prediccion = X_con_gastos[mask_prediccion]

# Realizar las predicciones para las filas con gastos faltantes
y_pred_gastos_faltantes = xgb_model.predict(X_prediccion)
y_pred_gastos_faltantes = np.round(y_pred_gastos_faltantes).astype(int)

# Asignar los valores predichos a la columna 'gastos'
df_final.loc[mask_prediccion, 'gastos'] = y_pred_gastos_faltantes

print("FASE 5 DONE: PREDICCIÓN DE COLUMNA EXTRAS")



#################### FASE 6: DETECCIÓN Y ELIMINACIÓN DE OUTLIERS CON XGBOOST EN VARIAS COLUMNAS ####################

# Preparar los datos (todas las características excepto las que vamos a predecir)
X = df_final[['aseos']].values  # Vamos a usar solo 'aseos' como variable predictora para simplificar

# Inicializar un DataFrame que almacene las máscaras de outliers para cada columna
mask_outliers_combined = pd.Series([False] * len(df_final), index=df_final.index)

# Definir una función para detectar y marcar outliers para una columna específica
def detectar_y_marcar_outliers(df_final, columna_objetivo):
    y = df_final[columna_objetivo].values

    # Dividir los datos en conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo XGBoost para predecir la columna objetivo
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    xgb_model.fit(X_train, y_train)

    # Realizar predicciones en todo el conjunto de datos
    y_pred_total = xgb_model.predict(X)

    # Calcular el error absoluto entre los valores reales y las predicciones
    error_absoluto_total = np.abs(y - y_pred_total)

    # Definir un umbral para identificar outliers (basado en 2 desviaciones estándar del error)
    umbral = np.mean(error_absoluto_total) + 2 * np.std(error_absoluto_total)

    # Identificar las filas que contienen outliers (filas con error mayor al umbral)
    mask_outliers = error_absoluto_total > umbral

    return mask_outliers

# Detectar y marcar outliers para cada columna
mask_outliers_precio = detectar_y_marcar_outliers(df_final, 'precio')
mask_outliers_superficie = detectar_y_marcar_outliers(df_final, 'superficie')
mask_outliers_habitaciones = detectar_y_marcar_outliers(df_final, 'habitaciones')

# Combinar las máscaras de outliers (si es outlier en alguna columna, será marcado como outlier)
mask_outliers_combined = mask_outliers_precio | mask_outliers_superficie | mask_outliers_habitaciones

# Eliminar las filas que contienen outliers en cualquier columna
df_sin_outliers = df_final[~mask_outliers_combined]

# Eliminar las filas que contienen valores vacíos (NaN)
df_sin_outliers = df_sin_outliers.dropna()

# Guardar el DataFrame sin outliers y sin valores vacíos en un archivo CSV
df_sin_outliers.to_csv('/opt/airflow/data/csv/datos_limpios.csv', index=False)

# Imprimir el resultado final
print(f"FASE 6 DONE: DETECCIÓN Y ELIMINACIÓN DE {np.sum(mask_outliers_combined)} OUTLIERS y NANS")
print("Proceso completado... Generado 'datos_limpios.csv'")