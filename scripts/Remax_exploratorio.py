import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from wordcloud import WordCloud
import re

# Función para cargar todos los CSVs que comienzan con 'Remax'
def cargar_datos_remax(carpeta='data/csv'):
    # Buscar archivos que comiencen con 'Remax' y terminen en '.csv'
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith('Remax') and archivo.endswith('.csv')]
    
    # Si no se encuentran archivos, lanzar un error
    if len(archivos_csv) == 0:
        raise ValueError("No se encontraron archivos CSV que comiencen con 'Remax'. Verifica la ruta y los archivos.")
    
    # Imprimir los archivos encontrados
    print("Archivos CSV encontrados:")
    for archivo in archivos_csv:
        print(archivo)
    
    # Cargar y concatenar los datos de los archivos CSV
    datos = pd.concat([pd.read_csv(archivo, delimiter='|') for archivo in archivos_csv], ignore_index=True)
    
    return datos

# Cargar los datos
df_remax = cargar_datos_remax()

# Análisis del tipo de datos en cada columna
print("\nAnálisis de tipos de datos:")
print(df_remax.info())

# 1. Distribución de Precios
plt.figure(figsize=(10, 6))
sns.histplot(df_remax['Precio'], bins=10, kde=True, color='blue')
plt.title('Distribución de Precios de Propiedades')
plt.xlabel('Precio (USD)')
plt.ylabel('Frecuencia')
plt.savefig('images/Remax/Remax_exp_precio_dist.png')
plt.show()

# 2. Relación entre Precio y Área
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Superficie Total (m²)', y='Precio', data=df_remax)
plt.title('Relación entre Precio y Superficie Total')
plt.xlabel('Superficie Total (m²)')
plt.ylabel('Precio (USD)')
plt.savefig('images/Remax/Remax_exp_precio_vs_superficie.png')
plt.show()

# 3. Distribución de Áreas
plt.figure(figsize=(10, 6))
sns.histplot(df_remax['Superficie Total (m²)'], bins=10, kde=True, color='green')
plt.title('Distribución de Superficie Total de Propiedades')
plt.xlabel('Superficie Total (m²)')
plt.ylabel('Frecuencia')
plt.savefig('images/Remax/Remax_exp_distribucion_superficie.png')
plt.show()

# 4. Relación entre Precio y Expensas
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Expensas', y='Precio', data=df_remax)
plt.title('Relación entre Expensas y Precio de Propiedades')
plt.xlabel('Expensas (USD)')
plt.ylabel('Precio (USD)')
plt.savefig('images/Remax/Remax_exp_precio_vs_expensas.png')
plt.show()

# 5. Distribución de Precios por Número de Ambientes
plt.figure(figsize=(10, 6))
sns.boxplot(x='Ambientes', y='Precio', data=df_remax)
plt.title('Distribución de Precios por Número de Ambientes')
plt.xlabel('Número de Ambientes')
plt.ylabel('Precio (USD)')
plt.savefig('images/Remax/Remax_exp_precio_por_ambientes.png')
plt.show()

# 6. Distribución de Precios por Número de Baños
plt.figure(figsize=(10, 6))
sns.boxplot(x='Baños', y='Precio', data=df_remax)
plt.title('Distribución de Precios por Número de Baños')
plt.xlabel('Número de Baños')
plt.ylabel('Precio (USD)')
plt.savefig('images/Remax/Remax_exp_precio_por_banos.png')
plt.show()

# 7. Clustering de Propiedades según Características Clave
# Seleccionar las características relevantes
features = df_remax[['Precio', 'Superficie Total (m²)', 'Baños', 'Ambientes']]
# Escalar los datos
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)
# Aplicar K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
df_remax['Cluster'] = kmeans.fit_predict(scaled_features)
# Visualizar los clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Superficie Total (m²)', y='Precio', hue='Cluster', data=df_remax, palette='viridis')
plt.title('Clustering de Propiedades por Precio y Superficie Total')
plt.savefig('images/Remax/Remax_exp_clustering.png')
plt.show()

# 8. Análisis de Discrepancia entre Superficie Total y Cubierta
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Superficie Total (m²)', y='Superficie Cubierta (m²)', data=df_remax)
plt.title('Relación entre Superficie Total y Superficie Cubierta')
plt.xlabel('Superficie Total (m²)')
plt.ylabel('Superficie Cubierta (m²)')
plt.savefig('images/Remax/Remax_exp_superficie_total_vs_cubierta.png')
plt.show()

# 9. Distribución de Precios por Agente
plt.figure(figsize=(10, 6))
sns.boxplot(x='Agente', y='Precio', data=df_remax)
plt.xticks(rotation=90)
plt.title('Distribución de Precios por Agente')
plt.xlabel('Agente')
plt.ylabel('Precio (USD)')
plt.savefig('images/Remax/Remax_exp_precio_por_agente.png')
plt.show()

# 10. Análisis de Palabras Clave en Descripciones
# Lista de palabras a eliminar
palabras_a_eliminar = ['departamento', 'venta', 'se vende', 'venta',  'de', 'en', 'con', 'el']
regex_patron = re.compile(r'\b(?:' + '|'.join(palabras_a_eliminar) + r')\b', flags=re.IGNORECASE)
# Unir todas las descripciones y eliminar las palabras no deseadas
texto_completo = ' '.join(df_remax['Descripción'].dropna())
texto_filtrado = regex_patron.sub('', texto_completo)
# Generar la nube de palabras
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto_filtrado)
# Mostrar la nube de palabras
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Palabras Más Comunes en Descripciones de Propiedades')
plt.savefig('images/Remax/Remax_exp_wordcloud_descripciones.png')
plt.show()