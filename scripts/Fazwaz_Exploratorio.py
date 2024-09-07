import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Función para cargar todos los CSVs que comienzan con 'FazWaz'
def cargar_datos_fazwaz(carpeta='data/csv'):
    # Buscar archivos que comiencen con 'Fazwaz' y terminen en '.csv'
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith('Fazwaz') and archivo.endswith('.csv')]
    
    # Si no se encuentran archivos, lanzar un error
    if len(archivos_csv) == 0:
        raise ValueError("No se encontraron archivos CSV que comiencen con 'Fazwaz'. Verifica la ruta y los archivos.")
    
    # Imprimir los archivos encontrados
    print("Archivos CSV encontrados:")
    for archivo in archivos_csv:
        print(archivo)
    
    # Cargar y concatenar los datos de los archivos CSV
    datos = pd.concat([pd.read_csv(archivo, delimiter='|') for archivo in archivos_csv], ignore_index=True)
    
    return datos

# Cargar los datos
df_fazwaz = cargar_datos_fazwaz()

# Análisis del tipo de datos en cada columna
print("\nAnálisis de tipos de datos:")
print(df_fazwaz.info())

# 1. Distribución de Precios
plt.figure(figsize=(10, 6))
sns.histplot(df_fazwaz['Precio'], bins=10, kde=True, color='blue')
plt.title('Distribución de Precios de Propiedades')
plt.xlabel('Precio (USD)')
plt.ylabel('Frecuencia')
plt.savefig('images/Fazwaz/Fazwaz_exp_precio_dist.png')
plt.show()

# 2. Distribución de Precio por m²
plt.figure(figsize=(10, 6))
sns.histplot(df_fazwaz['Precio por m²'], bins=10, kde=True, color='green')
plt.title('Distribución de Precio por m²')
plt.xlabel('Precio por m² (USD)')
plt.ylabel('Frecuencia')
plt.savefig('images/Fazwaz/Fazwaz_exp_precio_m2_dist.png')
plt.show()

# 3. Relación entre Precio y Área
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Área', y='Precio', data=df_fazwaz, hue='Habitaciones', palette='viridis')
plt.title('Relación entre Precio y Área')
plt.xlabel('Área (m²)')
plt.ylabel('Precio (USD)')
plt.savefig('images/Fazwaz/Fazwaz_exp_precio_vs_area.png')
plt.show()

# 4. Boxplot de Precios por Número de Habitaciones
plt.figure(figsize=(10, 6))
sns.boxplot(x='Habitaciones', y='Precio', data=df_fazwaz)
plt.title('Distribución de Precios por Número de Habitaciones')
plt.xlabel('Número de Habitaciones')
plt.ylabel('Precio (USD)')
plt.savefig('images/Fazwaz/Fazwaz_exp_precio_habitaciones_boxplot.png')
plt.show()

# 5. Heatmap de Correlación entre Variables Numéricas
plt.figure(figsize=(10, 6))
correlacion = df_fazwaz[['Precio', 'Precio por m²', 'Área', 'Habitaciones', 'Baños']].corr()
sns.heatmap(correlacion, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Heatmap de Correlación entre Variables Numéricas')
plt.savefig('images/Fazwaz/Fazwaz_exp_heatmap_correlacion.png')
plt.show()

# 6. Distribución de Habitaciones y Baños
# Distribución de Habitaciones
plt.figure(figsize=(8, 4))
sns.countplot(x='Habitaciones', data=df_fazwaz, palette='viridis')
plt.title('Distribución del Número de Habitaciones')
plt.savefig('images/Fazwaz/Fazwaz_exp_distribucion_habitaciones.png')
plt.show()

# Distribución de Baños
plt.figure(figsize=(8, 4))
sns.countplot(x='Baños', data=df_fazwaz, palette='viridis')
plt.title('Distribución del Número de Baños')
plt.savefig('images/Fazwaz/Fazwaz_exp_distribucion_baños.png')
plt.show()

# 7. Relación entre Precio y Área
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Área', y='Precio', data=df_fazwaz, hue='Habitaciones', palette='viridis')
plt.title('Relación entre Precio y Área')
plt.xlabel('Área (m²)')
plt.ylabel('Precio (USD)')
plt.savefig('images/Fazwaz/Fazwaz_exp_precio_vs_area.png')
plt.show()

# 8. Distribución de Precio por Metro Cuadrado según Ubicación
plt.figure(figsize=(10, 6))
sns.boxplot(x='Ubicación', y='Precio por m²', data=df_fazwaz)
plt.xticks(rotation=45)
plt.title('Distribución de Precio por m² según Ubicación')
plt.savefig('images/Fazwaz/Fazwaz_exp_precio_m2_vs_ubicacion.png')
plt.show()

# 9. Distribución de Amenidades (Extras)
df_extras = df_fazwaz['Extras'].dropna().str.split(', ')
all_extras = [extra for sublist in df_extras for extra in sublist]
extras_freq = pd.Series(all_extras).value_counts()

plt.figure(figsize=(10, 6))
sns.barplot(x=extras_freq.values, y=extras_freq.index, palette='viridis')
plt.title('Frecuencia de Amenidades en las Propiedades')
plt.savefig('images/Fazwaz/Fazwaz_exp_frecuencia_extras.png')
plt.show()

# 10. Segmentación de Mercado por Precio
bins = [0, 150000, 300000, 500000]
labels = ['Económico', 'Medio', 'Alto']
df_fazwaz['Segmento de Precio'] = pd.cut(df_fazwaz['Precio'], bins=bins, labels=labels)

plt.figure(figsize=(8, 4))
sns.countplot(x='Segmento de Precio', data=df_fazwaz, palette='magma')
plt.title('Distribución de Propiedades por Segmento de Precio')
plt.savefig('images/Fazwaz/Fazwaz_exp_segmento_precio.png')
plt.show()
