import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Función para cargar todos los CSVs que comienzan con 'Plusvalia'
def cargar_datos_plusvalia(carpeta='data/csv'):
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith('Plusvalia') and archivo.endswith('.csv')]
    if len(archivos_csv) == 0:
        raise ValueError("No se encontraron archivos CSV que comiencen con 'Plusvalia'. Verifica la ruta y los archivos.")
    print("Archivos CSV encontrados:")
    for archivo in archivos_csv:
        print(archivo)
    datos = pd.concat([pd.read_csv(archivo, delimiter='|') for archivo in archivos_csv], ignore_index=True)
    return datos

# Cargar los datos
df_plusvalia = cargar_datos_plusvalia()

# Análisis del tipo de datos en cada columna
print("\nAnálisis de tipos de datos:")
print(df_plusvalia.info())

df_plusvalia.describe()


# Extraer el barrio de la columna 'Ciudad'
df_plusvalia['Barrio'] = df_plusvalia['Ciudad'].apply(lambda x: x.split(',')[0].strip())

# Colores de la universidad
color_universidad_1 = (0/255, 32/255, 96/255)  # RGB (0, 32, 96)
color_universidad_2 = (247/255, 179/255, 9/255)  # RGB (247, 179, 9)

# 1. Distribución de Precios de las Propiedades
plt.figure(figsize=(10,6))
sns.histplot(df_plusvalia['Precio'], kde=False, color=color_universidad_1, bins=10)
plt.title('Distribución de Precios de las Propiedades')
plt.xlabel('Precio (USD)')
plt.ylabel('Frecuencia')
plt.axvline(df_plusvalia['Precio'].mean(), color='red', linestyle='--', label=f'Media: {int(df_plusvalia["Precio"].mean())} USD')
plt.legend()
plt.savefig('images/Plusvalia/Plusvalia_explo_distribucion_precios_propiedades.png')
plt.show()

# 2. Comparación de Precios entre Barrios
plt.figure(figsize=(12,8))
sns.boxplot(x='Precio', y='Barrio', data=df_plusvalia, hue='Barrio', palette='Blues', dodge=False)
plt.title('Comparación de Precios entre Barrios')
plt.xlabel('Precio (USD)')
plt.ylabel('Barrio')
plt.savefig('images/Plusvalia/Plusvalia_explo_comparacion_precios_barrios.png')
plt.show()

# 3. Relación entre Precio y Área
df_plusvalia['Área_Num'] = df_plusvalia['Área'].apply(lambda x: float(x.split('-')[0].strip()) if isinstance(x, str) else x)
plt.figure(figsize=(10,6))
sns.scatterplot(x='Área_Num', y='Precio', data=df_plusvalia, color=color_universidad_1, alpha=0.6)
plt.title('Relación entre Precio y Área')
plt.xlabel('Área (m²)')
plt.ylabel('Precio (USD)')
plt.savefig('images/Plusvalia/Plusvalia_explo_relacion_precio_area.png')
plt.show()

# 4. Detección de Outliers en Precios y Áreas en la misma gráfica
plt.figure(figsize=(14,6))
plt.subplot(1, 2, 1)
sns.boxplot(df_plusvalia['Precio'], color=color_universidad_1)
plt.title('Detección de Outliers en Precios de Propiedades')
plt.xlabel('Precio (USD)')
plt.subplot(1, 2, 2)
sns.boxplot(df_plusvalia['Área_Num'], color=color_universidad_2)
plt.title('Detección de Outliers en el Área de las Propiedades')
plt.xlabel('Área (m²)')
plt.tight_layout()
plt.savefig('images/Plusvalia/Plusvalia_explo_outliers_precio_area.png')
plt.show()

# 5. Distribución de Estacionamientos
df_plusvalia['Estacionamientos'] = df_plusvalia['Estacionamientos'].fillna(0).astype(int)
plt.figure(figsize=(8,6))
sns.histplot(df_plusvalia['Estacionamientos'], bins=5, color=color_universidad_2, kde=False)
plt.title('Distribución de Estacionamientos')
plt.xlabel('Número de Estacionamientos')
plt.ylabel('Frecuencia')
plt.savefig('images/Plusvalia/Plusvalia_explo_distribucion_estacionamientos.png')
plt.show()

# 6. Comparación de Cantidad de Amenidades por Barrio
lista_amenities = ['gimnasio', 'piscina', 'BBQ', 'seguridad', 'jardín', 'salón comunal', 
 'área de juegos', 'estacionamientos de visitas', 'jacuzzi', 'área de niños', 'terraza']
def contar_amenidades(descripcion):
    if isinstance(descripcion, str):
        return sum(amenity.lower() in descripcion.lower() for amenity in lista_amenities)
    return 0
df_plusvalia['Cantidad_Amenidades'] = df_plusvalia['Descripción'].apply(contar_amenidades)
amenidades_por_barrio = df_plusvalia.groupby('Barrio')['Cantidad_Amenidades'].mean().sort_values()
plt.figure(figsize=(12,8))
amenidades_por_barrio.plot(kind='barh', color=color_universidad_1)
plt.title('Promedio de Amenidades por Barrio (basado en Descripción)')
plt.xlabel('Promedio de Amenidades')
plt.ylabel('Barrio')
plt.grid(True, axis='x', linestyle='--')
plt.tight_layout()
plt.savefig('images/Plusvalia/Plusvalia_explo_amenidades_por_barrio.png')
plt.show()

# 7. Análisis de Rentabilidad por Metro Cuadrado
df_plusvalia['Precio_m2'] = df_plusvalia['Precio'] / df_plusvalia['Área_Num']
precio_m2_por_barrio = df_plusvalia.groupby('Barrio')['Precio_m2'].mean().sort_values(ascending=False)
plt.figure(figsize=(12,9))
precio_m2_por_barrio.plot(kind='bar', color=color_universidad_2)
plt.title('Precio Promedio por Metro Cuadrado en cada Barrio')
plt.ylabel('Precio Promedio por m² (USD)')
plt.xlabel('Barrio')
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.grid(axis='y', linestyle='--')
plt.savefig('images/Plusvalia/Plusvalia_explo_precio_m2_por_barrio.png')
plt.show()

# 8. Relación entre Habitaciones y Precio
df_plusvalia['Habitaciones_Num'] = df_plusvalia['Habitaciones'].apply(lambda x: float(x.split('-')[0].strip()) if isinstance(x, str) else x)
plt.figure(figsize=(10,6))
sns.scatterplot(x='Habitaciones_Num', y='Precio', data=df_plusvalia, color=color_universidad_2)
plt.title('Relación entre Número de Habitaciones y Precio de las Propiedades')
plt.xlabel('Número de Habitaciones')
plt.ylabel('Precio (USD)')
plt.grid(True)
plt.savefig('images/Plusvalia/Plusvalia_explo_relacion_habitaciones_precio.png')
plt.show()

# 9. Análisis de Variación de Tamaño de las Propiedades por Barrio
df_plusvalia['Área_Num'] = df_plusvalia['Área'].apply(lambda x: float(x.split('-')[0].strip()) if isinstance(x, str) else x)
area_por_barrio = df_plusvalia.groupby('Barrio')['Área_Num'].mean().sort_values(ascending=False)
plt.figure(figsize=(12,9))
area_por_barrio.plot(kind='bar', color=color_universidad_2)
plt.title('Área Promedio por Barrio')
plt.ylabel('Área Promedio (m²)')
plt.xlabel('Barrio')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--')
plt.savefig('images/Plusvalia/Plusvalia_explo_area_promedio_por_barrio.png')
plt.show()

# 10. Análisis de la Variación de Expensas:
df_plusvalia['Expensas'] = df_plusvalia['Expensas'].replace('N/A', 0).astype(float)
plt.figure(figsize=(10,6))
sns.scatterplot(x='Expensas', y='Precio', data=df_plusvalia, color='purple')
plt.title('Relación entre Expensas y Precio de la Propiedad')
plt.xlabel('Expensas (USD)')
plt.ylabel('Precio (USD)')
plt.grid(True)
plt.savefig('images/Plusvalia/Plusvalia_explo_expensas_vs_precio.png')
plt.show()
