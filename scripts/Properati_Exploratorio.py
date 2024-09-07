import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Función para cargar los CSVs de Properati
def cargar_datos_properati(carpeta='data/csv'):
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith('Properati') and archivo.endswith('.csv')]
    
    if len(archivos_csv) == 0:
        raise ValueError("No se encontraron archivos CSV que comiencen con 'Properati'. Verifica la ruta y los archivos.")
    
    print("Archivos CSV encontrados:")
    for archivo in archivos_csv:
        print(archivo)
    
    datos = pd.concat([pd.read_csv(archivo, delimiter='|') for archivo in archivos_csv], ignore_index=True)
    
    return datos

# Cargar los datos de Properati
df_properati = cargar_datos_properati()

# Análisis del tipo de datos en cada columna
print("\nAnálisis de tipos de datos:")
print(df_properati.info())

# Preprocesar la columna de ubicación para extraer solo el barrio (primer elemento antes de las comas)
df_properati['Barrio'] = df_properati['Ubicación'].apply(lambda x: x.split(',')[0].strip())

# 1. Distribución de Precios
plt.figure(figsize=(10, 6))
sns.histplot(df_properati['Precio'], bins=10, kde=True, color='blue')
plt.title('Distribución de Precios de Propiedades')
plt.xlabel('Precio (USD)')
plt.ylabel('Frecuencia')
plt.savefig('images/Properati/Properati_exp_precio_dist.png')
plt.show()

# 2. Relación entre Precio y Área
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Área', y='Precio', data=df_properati)
plt.title('Relación entre Precio y Área')
plt.xlabel('Área (m²)')
plt.ylabel('Precio (USD)')
plt.savefig('images/Properati/Properati_exp_precio_vs_area.png')
plt.show()

# 3. Distribución de Áreas
plt.figure(figsize=(10, 6))
sns.histplot(df_properati['Área'], bins=10, kde=True, color='green')
plt.title('Distribución de Áreas de Propiedades')
plt.xlabel('Área (m²)')
plt.ylabel('Frecuencia')
plt.savefig('images/Properati/Properati_exp_distribucion_areas.png')
plt.show()

# 4. Distribución de Precios por Número de Habitaciones
plt.figure(figsize=(10, 6))
sns.boxplot(x='Habitaciones', y='Precio', data=df_properati)
plt.title('Distribución de Precios por Número de Habitaciones')
plt.xlabel('Número de Habitaciones')
plt.ylabel('Precio (USD)')
plt.savefig('images/Properati/Properati_exp_precio_por_habitaciones.png')
plt.show()

# 5. Distribución del Número de Baños
plt.figure(figsize=(10, 6))
sns.countplot(x='Baños', data=df_properati)
plt.title('Distribución del Número de Baños')
plt.xlabel('Número de Baños')
plt.ylabel('Frecuencia')
plt.savefig('images/Properati/Properati_exp_distribucion_banos.png')
plt.show()

# 6. Distribución de Precios por Barrio (Ubicación ajustada)
plt.figure(figsize=(10, 6))
sns.boxplot(x='Barrio', y='Precio', data=df_properati)
plt.title('Distribución de Precios por Barrio')
plt.xticks(rotation=45, ha='right')
plt.xlabel('Barrio')
plt.ylabel('Precio (USD)')
plt.savefig('images/Properati/Properati_exp_precio_por_barrio.png')
plt.show()

# 7. Distribución de Habitaciones
plt.figure(figsize=(8, 6))
sns.countplot(x='Habitaciones', data=df_properati)
plt.title('Distribución del Número de Habitaciones')
plt.xlabel('Número de Habitaciones')
plt.ylabel('Frecuencia')
plt.savefig('images/Properati/Properati_exp_distribucion_habitaciones.png')
plt.show()

# 8. Distribución de Precios por Agencia
plt.figure(figsize=(10, 6))
sns.boxplot(x='Agencia', y='Precio', data=df_properati)
plt.title('Distribución de Precios por Agencia')
plt.xticks(rotation=90, ha='right')
plt.xlabel('Agencia')
plt.ylabel('Precio (USD)')
plt.savefig('images/Properati/Properati_exp_precio_por_agencia.png')
plt.show()

# 9. Relación entre Área y Número de Habitaciones
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Área', y='Habitaciones', data=df_properati, hue='Baños', palette='viridis')
plt.title('Relación entre Área y Número de Habitaciones')
plt.xlabel('Área (m²)')
plt.ylabel('Número de Habitaciones')
plt.savefig('images/Properati/Properati_exp_area_vs_habitaciones.png')
plt.show()

# 10. Heatmap de Correlación entre Variables Numéricas
plt.figure(figsize=(10, 6))
correlacion = df_properati[['Precio', 'Área', 'Habitaciones', 'Baños']].corr()
sns.heatmap(correlacion, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Heatmap de Correlación entre Variables Numéricas')
plt.savefig('images/Properati/Properati_exp_heatmap_correlacion.png')
plt.show()
