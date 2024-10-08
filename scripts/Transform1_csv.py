import os
from datetime import datetime
import spacy
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import FunctionTransformer  # <--- Este es el import que faltaba
from sklearn.metrics import r2_score, mean_squared_error, make_scorer
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split


# Función para cargar los datos de una inmobiliaria específica y extraer la fecha de captura
def cargar_datos_inmobiliaria(inmobiliaria, carpeta='data/csv'):
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
def procesar_todas_inmobiliarias(carpeta='data/csv'):
    inmobiliarias = ['Fazwaz', 'Mitula', 'Properati', 'Remax']
    datos_totales = pd.DataFrame()

    for inmobiliaria in inmobiliarias:
        df = cargar_datos_inmobiliaria(inmobiliaria, carpeta)
        df_preparado = procesar_inmobiliaria(df, inmobiliaria)
        datos_totales = pd.concat([datos_totales, df_preparado], ignore_index=True)
    
    return datos_totales

# Procesar todos los datos
df_final = procesar_todas_inmobiliarias()

# Función para convertir precios, habitaciones y gastos a enteros
def convertir_a_entero(valor):
    try:
        return int(float(valor)) if valor != '' else None
    except ValueError:
        return None

# Función para convertir área, aseos (Baños) a flotante
def convertir_a_float(valor):
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

# Estandarizar las columnas precio, habitaciones, gastos como enteros y aseos como float
df_final['precio'] = df_final['precio'].apply(convertir_a_entero)
df_final['habitaciones'] = df_final['habitaciones'].apply(convertir_a_entero)
df_final['gastos'] = df_final['gastos'].apply(convertir_a_entero)
df_final['aseos'] = df_final['aseos'].apply(convertir_a_float)
df_final['captura'] = df_final['captura'].apply(convertir_fecha)

# Guardar el DataFrame estandarizado
df_final.to_csv('data/csv/Transform1_std.csv', index=False)

# Análisis de valores nulos
missing_values = df_final.isnull().sum()

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

    match_habitaciones = re.search(r'(\d+)\s*(?:a\s*(\d+)\s*)?(habitación|dormitorio|recámara|cuarto|hab)', texto, re.IGNORECASE)
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
df_final.to_csv('data/csv/Transform1_enriquecido.csv', index=False)

# Lista de extras valiosos
extras_valiosos = [
    'piscina', 'terraza', 'barbacoa', 'bbq', 'gimnasio', 
    'jacuzzi', 'spa', 'sauna', 'parqueadero', 'garaje', 
    'bodega', 'balcón', 'ascensor', 'zona de juegos', 
    'pista de correr', 'áreas verdes', 'circuito cerrado de cámaras',
    'chimenea', 'conserje', 'garita de guardianía', 
    'acceso para personas con discapacidad', 'patio', 
    'vista panorámica', 'seguridad', 'cuarto de servicio', 
    'internet', 'alarma', 'calefacción', 'cancha de tenis', 
    'completamente amoblado', 'zona bbq', 'sin amoblar', 
    'jardín', 'piscina privada', 'gimnasio privado', 'estacionamiento'
]

# Filtrar los extras que aportan valor
def filtrar_extras_valiosos(texto_extras, extras_valiosos):
    texto_extras = texto_extras.lower() 
    extras_filtrados = [extra for extra in extras_valiosos if extra in texto_extras]
    return ', '.join(extras_filtrados) if extras_filtrados else None

def procesar_extras_y_filtrar(row):
    texto_extras = str(row['extras']).lower()
    extras_valiosos_filtrados = filtrar_extras_valiosos(texto_extras, extras_valiosos)
    row['extras'] = extras_valiosos_filtrados
    return row

# Aplicar el procesamiento de extras para filtrar los que aportan valor
df_final = df_final.apply(procesar_extras_y_filtrar, axis=1)

# Guardar el DataFrame actualizado con los extras filtrados
df_final.to_csv('data/csv/Transform1_extras_filtrados.csv', index=False)

print("Proceso completado. Archivo 'Transform1_extras_filtrados' generado.")

#######################  PREDICCIÓN DE GASTOS   #############################

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

# Calcular el coeficiente de determinación (R^2) y RMSE en el conjunto de prueba
r2 = r2_score(y_test_split, y_pred_split)
rmse = mean_squared_error(y_test_split, y_pred_split, squared=False)

# Mostrar los resultados del modelo entrenado
print(f"R^2 XGBoost en prueba: {r2}")
print(f"RMSE XGBoost en prueba: {rmse}")

# Predecir los valores faltantes de gastos (donde gastos es NaN)
mask_prediccion = np.isnan(y_con_gastos)
X_prediccion = X_con_gastos[mask_prediccion]

# Realizar las predicciones para las filas con gastos faltantes
y_pred_gastos_faltantes = xgb_model.predict(X_prediccion)
y_pred_gastos_faltantes = np.round(y_pred_gastos_faltantes).astype(int)

# Asignar los valores predichos a la columna 'gastos'
df_final.loc[mask_prediccion, 'gastos'] = y_pred_gastos_faltantes

# Guardar el DataFrame actualizado con los valores de gastos completados
df_final.to_csv('data/csv/Transform1_gastos_completados.csv', index=False)

print("Proceso completado. Archivo 'Transform1_gastos_completados' generado.")

############### Identificar outliers en precio, aseos, superficie, habitaciones y gastos ###############

def identificar_outliers(df, columna):
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    outliers = df_final[(df[columna] < limite_inferior) | (df[columna] > limite_superior)]
    return outliers

outliers_precio = identificar_outliers(df_final, 'precio')
outliers_aseos = identificar_outliers(df_final, 'aseos')
outliers_superficie = identificar_outliers(df_final, 'superficie')
outliers_habitaciones = identificar_outliers(df_final, 'habitaciones')
outliers_gastos = identificar_outliers(df_final, 'gastos')

print("Outliers en precio:", outliers_precio)
print("Outliers en aseos:", outliers_aseos)
print("Outliers en superficie:", outliers_superficie)
print("Outliers en habitaciones:", outliers_habitaciones)
print("Outliers en gastos:", outliers_gastos)

####################  DETECCIÓN Y ELIMINACIÓN DE OUTLIERS   ####################

# Cargar el CSV con los datos completados
df = pd.read_csv('data/csv/Transform1_gastos_completados.csv')

# Variables que deseas analizar
variables = ['precio', 'superficie', 'habitaciones', 'aseos', 'gastos']

# Función para detectar outliers
def detectar_outliers(df, columna):
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    return limite_inferior, limite_superior

# Aplicar transformación logarítmica para 'precio' y 'superficie'
transformer = FunctionTransformer(np.log1p, validate=True, feature_names_out='one-to-one')
df[['precio', 'superficie']] = transformer.fit_transform(df[['precio', 'superficie']])

# Detectar outliers después de la transformación logarítmica
for variable in ['precio', 'superficie']:
    limite_inferior, limite_superior = detectar_outliers(df, variable)
    print(f'Outliers en {variable} después de log transform: Menores a {limite_inferior} o mayores a {limite_superior}')

# Detectar outliers en otras variables sin transformación logarítmica
for variable in ['habitaciones', 'aseos', 'gastos']:
    limite_inferior, limite_superior = detectar_outliers(df, variable)
    print(f'Outliers en {variable}: Menores a {limite_inferior} o mayores a {limite_superior}')

# Definir rangos lógicos para eliminar outliers
rangos_logicos = {
    'precio': {'min': np.log1p(50000), 'max': np.log1p(500000)},
    'superficie': {'min': np.log1p(20), 'max': np.log1p(1000)},
    'habitaciones': {'min': 1, 'max': 10},
    'gastos': {'min': 0, 'max': 500}
}

# Aplicar rangos lógicos
df_filtrado = df[(df['precio'] >= rangos_logicos['precio']['min']) & (df['precio'] <= rangos_logicos['precio']['max'])]
df_filtrado = df_filtrado[(df_filtrado['superficie'] >= rangos_logicos['superficie']['min']) & (df_filtrado['superficie'] <= rangos_logicos['superficie']['max'])]
df_filtrado = df_filtrado[(df_filtrado['habitaciones'] >= rangos_logicos['habitaciones']['min']) & (df_filtrado['habitaciones'] <= rangos_logicos['habitaciones']['max'])]
df_filtrado = df_filtrado[(df_filtrado['gastos'] >= rangos_logicos['gastos']['min']) & (df_filtrado['gastos'] <= rangos_logicos['gastos']['max'])]

# Revertir la transformación logarítmica
df_filtrado[['precio', 'superficie']] = transformer.inverse_transform(df_filtrado[['precio', 'superficie']])

# Guardar el DataFrame filtrado en un nuevo CSV
df_filtrado.to_csv('data/csv/Transform1_filtrado.csv', index=False)
print("Proceso completado. Archivo 'Transform1_filtrado.csv' generado.")

# Visualización de distribuciones después de la eliminación de outliers
import seaborn as sns
import matplotlib.pyplot as plt

for variable in variables:
    plt.figure(figsize=(10, 4))

    # Histograma
    plt.subplot(1, 2, 1)
    sns.histplot(df_filtrado[variable], kde=True)
    plt.title(f'Distribución de {variable} después del filtrado')

    # Boxplot
    plt.subplot(1, 2, 2)
    sns.boxplot(x=df_filtrado[variable])
    plt.title(f'Boxplot de {variable} después del filtrado')

    # Guardar los gráficos en la carpeta 'images'
    plt.tight_layout()
    plt.savefig(f'images/{variable}_despues_filtrado.png')
    plt.close()

# Continuar con el entrenamiento del modelo XGBoost después de eliminar los outliers
X = df_filtrado[['superficie', 'habitaciones', 'aseos']].values
y = df_filtrado['gastos'].values

# División de los datos
X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenamiento del modelo XGBoost
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
xgb_model.fit(X_train_split, y_train_split)

# Evaluación del modelo después de eliminar los outliers
y_pred_split = xgb_model.predict(X_test_split)
r2_post_filtrado = r2_score(y_test_split, y_pred_split)
rmse_post_filtrado = mean_squared_error(y_test_split, y_pred_split, squared=False)

# Mostrar los resultados después de eliminar los outliers
print(f"R^2 después de eliminar outliers: {r2_post_filtrado}")
print(f"RMSE después de eliminar outliers: {rmse_post_filtrado}")
