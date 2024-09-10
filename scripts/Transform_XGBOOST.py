##########################################################
# Sección 1: Detección y Eliminación de Outliers
##########################################################

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import r2_score, mean_squared_error, make_scorer
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# Cargar el CSV con datos estandarizados
df = pd.read_csv('data/csv/Transform1_gastos_completados.csv')

# Variables que deseas analizar
variables = ['precio', 'superficie', 'habitaciones', 'aseos', 'gastos']

# Función para calcular los límites superior e inferior usando el IQR (con estadística robusta)
def detectar_outliers(df, columna):
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    return limite_inferior, limite_superior

# Aplicar transformación logarítmica para variables 'precio' y 'superficie'
transformer = FunctionTransformer(np.log1p, validate=True, feature_names_out='one-to-one')
df[['precio', 'superficie']] = transformer.fit_transform(df[['precio', 'superficie']])

# Detectar outliers para cada variable después de la transformación logarítmica
for variable in ['precio', 'superficie']:
    limite_inferior, limite_superior = detectar_outliers(df, variable)
    print(f'Outliers en {variable} después de log transform: Menores a {limite_inferior} o mayores a {limite_superior}')

# Detectar outliers en las otras variables sin transformación logarítmica
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

# Función para aplicar rangos lógicos y eliminar outliers
def aplicar_rangos_logicos(df, rangos):
    for columna, limites in rangos.items():
        df = df[(df[columna] >= limites['min']) & (df[columna] <= limites['max'])]
    return df

# Aplicar rangos lógicos
df_filtrado = aplicar_rangos_logicos(df, rangos_logicos)

# Revertir la transformación logarítmica
df_filtrado[['precio', 'superficie']] = transformer.inverse_transform(df_filtrado[['precio', 'superficie']])

# Guardar el DataFrame filtrado
df_filtrado.to_csv('images/Transform1_filtrado.csv', index=False)
print("Proceso completado. Archivo 'Transform1_filtrado.csv' generado.")

# Visualización de las distribuciones después de eliminar los outliers
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

    # Guardar el gráfico en la carpeta 'images'
    plt.tight_layout()
    plt.savefig(f'images/{variable}_despues_filtrado.png')
    plt.close()

##########################################################
# Sección 2: Entrenamiento del Modelo XGBoost con Outliers Eliminados
##########################################################

# Dividir nuevamente los datos para el modelo después de la limpieza de outliers
X = df_filtrado[['superficie', 'habitaciones', 'aseos']].values
y = df_filtrado['gastos'].values

X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar el modelo XGBoost
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
xgb_model.fit(X_train_split, y_train_split)

# Evaluar el modelo después de eliminar los outliers
y_pred_split = xgb_model.predict(X_test_split)
r2_post_filtrado = r2_score(y_test_split, y_pred_split)
rmse_post_filtrado = mean_squared_error(y_test_split, y_pred_split, squared=False)

# Mostrar los resultados después de eliminar los outliers
print(f"R^2 después de eliminar outliers: {r2_post_filtrado}")
print(f"RMSE después de eliminar outliers: {rmse_post_filtrado}")














no se si sea neceasrio en fase 5:

# Calcular el coeficiente de determinación (R^2) y RMSE en el conjunto de prueba
r2 = r2_score(y_test_split, y_pred_split)
rmse = mean_squared_error(y_test_split, y_pred_split, squared=False)

# Mostrar los resultados del modelo entrenado
print(f"R^2 XGBoost en prueba: {r2}")
print(f"RMSE XGBoost en prueba: {rmse}")

iba en medio de estos:# Realizar predicciones en el conjunto de prueba
y_pred_split = xgb_model.predict(X_test_split)

# Predecir los valores faltantes de gastos (donde gastos es NaN)
mask_prediccion = np.isnan(y_con_gastos)
X_prediccion = X_con_gastos[mask_prediccion]












mas apuntes

############## Identificar outliers en precio, aseos, superficie, habitaciones y gastos ###############

# Función para identificar outliers utilizando el método del rango intercuartílico (IQR)
def identificar_outliers(df_final, columna):
    # Calcular el primer y tercer cuartil
    Q1 = df_final[columna].quantile(0.25)
    Q3 = df_final[columna].quantile(0.75)
    # Rango intercuartílico (IQR)
    IQR = Q3 - Q1
    # Límites inferior y superior para identificar outliers
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    # Filtrar filas que estén fuera de los límites
    outliers = df_final[(df_final[columna] < limite_inferior) | (df_final[columna] > limite_superior)]
    return outliers

# Detectar outliers en diferentes columnas
outliers_precio = identificar_outliers(df_final, 'precio')
outliers_aseos = identificar_outliers(df_final, 'aseos')
outliers_superficie = identificar_outliers(df_final, 'superficie')
outliers_habitaciones = identificar_outliers(df_final, 'habitaciones')
outliers_gastos = identificar_outliers(df_final, 'gastos')

# Imprimir los outliers detectados
print("Outliers en precio:", outliers_precio)
print("Outliers en aseos:", outliers_aseos)
print("Outliers en superficie:", outliers_superficie)
print("Outliers en habitaciones:", outliers_habitaciones)
print("Outliers en gastos:", outliers_gastos)

####################  DETECCIÓN Y ELIMINACIÓN DE OUTLIERS   ####################

# Variables que deseas analizar
variables = ['precio', 'superficie', 'habitaciones', 'aseos', 'gastos']

# Función para detectar los límites de outliers utilizando IQR
def detectar_outliers(df_final, columna):
    Q1 = df_final[columna].quantile(0.25)
    Q3 = df_final[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    return limite_inferior, limite_superior

# Aplicar transformación logarítmica para 'precio' y 'superficie'
transformer = FunctionTransformer(np.log1p, validate=True, feature_names_out='one-to-one')
df_final[['precio', 'superficie']] = transformer.fit_transform(df_final[['precio', 'superficie']])

# Detectar outliers después de la transformación logarítmica
for variable in ['precio', 'superficie']:
    limite_inferior, limite_superior = detectar_outliers(df_final, variable)
    print(f'Outliers en {variable} después de la transformación logarítmica: Menores a {limite_inferior} o mayores a {limite_superior}')

# Detectar outliers en variables que no usan transformación logarítmica
for variable in ['habitaciones', 'aseos', 'gastos']:
    limite_inferior, limite_superior = detectar_outliers(df_final, variable)
    print(f'Outliers en {variable}: Menores a {limite_inferior} o mayores a {limite_superior}')

# Definir rangos lógicos predefinidos para eliminar outliers
rangos_logicos = {
    'precio': {'min': np.log1p(50000), 'max': np.log1p(500000)},
    'superficie': {'min': np.log1p(20), 'max': np.log1p(1000)},
    'habitaciones': {'min': 1, 'max': 10},
    'gastos': {'min': 0, 'max': 500}
}

# Aplicar los rangos lógicos para filtrar outliers
df_filtrado = df_final[(df_final['precio'] >= rangos_logicos['precio']['min']) & (df_final['precio'] <= rangos_logicos['precio']['max'])]
df_filtrado = df_filtrado[(df_filtrado['superficie'] >= rangos_logicos['superficie']['min']) & (df_filtrado['superficie'] <= rangos_logicos['superficie']['max'])]
df_filtrado = df_filtrado[(df_filtrado['habitaciones'] >= rangos_logicos['habitaciones']['min']) & (df_filtrado['habitaciones'] <= rangos_logicos['habitaciones']['max'])]
df_filtrado = df_filtrado[(df_filtrado['gastos'] >= rangos_logicos['gastos']['min']) & (df_filtrado['gastos'] <= rangos_logicos['gastos']['max'])]

# Revertir la transformación logarítmica para 'precio' y 'superficie'
df_filtrado[['precio', 'superficie']] = transformer.inverse_transform(df_filtrado[['precio', 'superficie']])

# Guardar el DataFrame filtrado en un nuevo CSV
df_filtrado.to_csv('data/csv/Transform1_filtrado.csv', index=False)
print("Proceso completado. Archivo 'Transform1_filtrado.csv' generado.")

#################### Visualización de distribuciones después de la eliminación de outliers ####################

# Visualización con histogramas y boxplots después de eliminar outliers
import seaborn as sns
import matplotlib.pyplot as plt

for variable in variables:
    plt.figure(figsize=(10, 4))

    # Histograma de la variable
    plt.subplot(1, 2, 1)
    sns.histplot(df_filtrado[variable], kde=True)
    plt.title(f'Distribución de {variable} después del filtrado')

    # Boxplot de la variable
    plt.subplot(1, 2, 2)
    sns.boxplot(x=df_filtrado[variable])
    plt.title(f'Boxplot de {variable} después del filtrado')

    # Guardar los gráficos en la carpeta 'images'
    plt.tight_layout()
    plt.savefig(f'images/{variable}_despues_filtrado.png')
    plt.close()

#################### Entrenamiento del modelo XGBoost después de eliminar los outliers ####################

# Preparar datos para el modelo
X = df_filtrado[['superficie', 'habitaciones', 'aseos']].values
y = df_filtrado['gastos'].values

# División de los datos en entrenamiento y prueba
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

# Método IQR para detectar outliers
def detectar_outliers_iqr(df, columna):
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    return df[(df[columna] < limite_inferior) | (df[columna] > limite_superior)]

# Detectar outliers con IQR
outliers_precio_iqr = detectar_outliers_iqr(df_final, 'precio')
outliers_superficie_iqr = detectar_outliers_iqr(df_final, 'superficie')
outliers_habitaciones_iqr = detectar_outliers_iqr(df_final, 'habitaciones')
outliers_aseos_iqr = detectar_outliers_iqr(df_final, 'aseos')

# Visualización de los resultados del método IQR
print(f"Outliers en precio (IQR): {len(outliers_precio_iqr)}")
print(f"Outliers en superficie (IQR): {len(outliers_superficie_iqr)}")
print(f"Outliers en habitaciones (IQR): {len(outliers_habitaciones_iqr)}")
print(f"Outliers en aseos (IQR): {len(outliers_aseos_iqr)}")


from scipy import stats

# Método Z-Score para detectar outliers
def detectar_outliers_zscore(df, columna):
    z_scores = stats.zscore(df[columna])
    return df[(abs(z_scores) > 3)]

# Detectar outliers con Z-Score
outliers_precio_zscore = detectar_outliers_zscore(df_final, 'precio')
outliers_superficie_zscore = detectar_outliers_zscore(df_final, 'superficie')
outliers_habitaciones_zscore = detectar_outliers_zscore(df_final, 'habitaciones')
outliers_aseos_zscore = detectar_outliers_zscore(df_final, 'aseos')

# Visualización de los resultados del método Z-Score
print(f"Outliers en precio (Z-Score): {len(outliers_precio_zscore)}")
print(f"Outliers en superficie (Z-Score): {len(outliers_superficie_zscore)}")
print(f"Outliers en habitaciones (Z-Score): {len(outliers_habitaciones_zscore)}")
print(f"Outliers en aseos (Z-Score): {len(outliers_aseos_zscore)}")


from sklearn.cluster import DBSCAN
import numpy as np

# Método DBSCAN para detectar outliers
def detectar_outliers_dbscan(df, columnas):
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    data = df[columnas].values
    labels = dbscan.fit_predict(data)
    return df[labels == -1]  # Los outliers son aquellos con label -1

# Detectar outliers con DBSCAN
outliers_dbscan = detectar_outliers_dbscan(df_final, ['precio', 'superficie', 'habitaciones', 'aseos'])

# Visualización de los resultados del método DBSCAN
print(f"Outliers detectados con DBSCAN: {len(outliers_dbscan)}")






y mas apuntes

########################### FASE 6: DETECCIÓN Y ELIMINACIÓN DE OUTLIERS ###########################

# Importar las librerías necesarias
import pandas as pd
import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error

############### Identificar outliers en precio, aseos, superficie, habitaciones y gastos ###############

# Función para identificar outliers utilizando el método del rango intercuartílico (IQR)
def identificar_outliers(df_final, columna):
    # Calcular el primer y tercer cuartil
    Q1 = df_final[columna].quantile(0.25)
    Q3 = df_final[columna].quantile(0.75)
    # Rango intercuartílico (IQR)
    IQR = Q3 - Q1
    # Límites inferior y superior para identificar outliers
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    # Filtrar filas que estén fuera de los límites
    outliers = df_final[(df_final[columna] < limite_inferior) | (df_final[columna] > limite_superior)]
    return outliers

# Detectar outliers en diferentes columnas
outliers_precio = identificar_outliers(df_final, 'precio')
outliers_aseos = identificar_outliers(df_final, 'aseos')
outliers_superficie = identificar_outliers(df_final, 'superficie')
outliers_habitaciones = identificar_outliers(df_final, 'habitaciones')
outliers_gastos = identificar_outliers(df_final, 'gastos')

# Imprimir los outliers detectados
print("Outliers en precio:", outliers_precio)
print("Outliers en aseos:", outliers_aseos)
print("Outliers en superficie:", outliers_superficie)
print("Outliers en habitaciones:", outliers_habitaciones)
print("Outliers en gastos:", outliers_gastos)

#################### DETECCIÓN Y ELIMINACIÓN DE OUTLIERS ####################

# Variables que deseas analizar
variables = ['precio', 'superficie', 'habitaciones', 'aseos', 'gastos']

# Función para detectar los límites de outliers utilizando IQR
def detectar_outliers(df_final, columna):
    Q1 = df_final[columna].quantile(0.25)
    Q3 = df_final[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    return limite_inferior, limite_superior

# Aplicar transformación logarítmica para 'precio' y 'superficie'
transformer = FunctionTransformer(np.log1p, validate=True, feature_names_out='one-to-one')
df_final[['precio', 'superficie']] = transformer.fit_transform(df_final[['precio', 'superficie']])

# Detectar outliers después de la transformación logarítmica
for variable in ['precio', 'superficie']:
    limite_inferior, limite_superior = detectar_outliers(df_final, variable)
    print(f'Outliers en {variable} después de la transformación logarítmica: Menores a {limite_inferior} o mayores a {limite_superior}')

# Detectar outliers en variables que no usan transformación logarítmica
for variable in ['habitaciones', 'aseos', 'gastos']:
    limite_inferior, limite_superior = detectar_outliers(df_final, variable)
    print(f'Outliers en {variable}: Menores a {limite_inferior} o mayores a {limite_superior}')

# Definir rangos lógicos predefinidos para eliminar outliers
rangos_logicos = {
    'precio': {'min': np.log1p(50000), 'max': np.log1p(500000)},
    'superficie': {'min': np.log1p(20), 'max': np.log1p(1000)},
    'habitaciones': {'min': 1, 'max': 10},
    'gastos': {'min': 0, 'max': 500}
}

# Aplicar los rangos lógicos para filtrar outliers
df_filtrado = df_final[(df_final['precio'] >= rangos_logicos['precio']['min']) & (df_final['precio'] <= rangos_logicos['precio']['max'])]
df_filtrado = df_filtrado[(df_filtrado['superficie'] >= rangos_logicos['superficie']['min']) & (df_filtrado['superficie'] <= rangos_logicos['superficie']['max'])]
df_filtrado = df_filtrado[(df_filtrado['habitaciones'] >= rangos_logicos['habitaciones']['min']) & (df_filtrado['habitaciones'] <= rangos_logicos['habitaciones']['max'])]
df_filtrado = df_filtrado[(df_filtrado['gastos'] >= rangos_logicos['gastos']['min']) & (df_filtrado['gastos'] <= rangos_logicos['gastos']['max'])]

# Revertir la transformación logarítmica para 'precio' y 'superficie'
df_filtrado[['precio', 'superficie']] = transformer.inverse_transform(df_filtrado[['precio', 'superficie']])

# Guardar el DataFrame filtrado en un nuevo CSV
df_filtrado.to_csv('data/csv/Transform1_filtrado.csv', index=False)
print("Proceso completado. Archivo 'Transform1_filtrado.csv' generado.")

#################### Visualización de distribuciones después de la eliminación de outliers ####################

# Visualización con histogramas y boxplots después de eliminar outliers
import seaborn as sns
import matplotlib.pyplot as plt

for variable in variables:
    plt.figure(figsize=(10, 4))

    # Histograma de la variable
    plt.subplot(1, 2, 1)
    sns.histplot(df_filtrado[variable], kde=True)
    plt.title(f'Distribución de {variable} después del filtrado')

    # Boxplot de la variable
    plt.subplot(1, 2, 2)
    sns.boxplot(x=df_filtrado[variable])
    plt.title(f'Boxplot de {variable} después del filtrado')

    # Guardar los gráficos en la carpeta 'images'
    plt.tight_layout()
    plt.savefig(f'images/{variable}_despues_filtrado.png')
    plt.close()

#################### Entrenamiento del modelo XGBoost después de eliminar los outliers ####################

# Preparar datos para el modelo
X = df_filtrado[['superficie', 'habitaciones', 'aseos']].values
y = df_filtrado['gastos'].values

# División de los datos en entrenamiento y prueba
X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenamiento del modelo XGBoost
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
xgb_model.fit(X_train_split, y_train_split)

# Evaluación del modelo después de eliminar los outliers
y_pred_split = xgb_model.predict(X_test_split)
r2_post_filtrado = r2_score(y_test_split, y_pred_split)
rmse_post_filtrado = mean_squared_error(y_test_split, y_pred_split, squared=False)

# Mostrar los resultados después de eliminar los outliers
print(f"R² después de eliminar outliers: {r2_post_filtrado}")
print(f"RMSE después de eliminar outliers: {rmse_post_filtrado}")
