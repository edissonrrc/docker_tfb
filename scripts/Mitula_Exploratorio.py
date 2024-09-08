import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Función para cargar todos los CSVs que comienzan con 'Mitula'
def cargar_datos_mitula(carpeta='data/csv'):
    # Buscar archivos que comiencen con 'Mitula' y terminen en '.csv'
    archivos_csv = [os.path.join(carpeta, archivo) for archivo in os.listdir(carpeta) if archivo.startswith('Mitula') and archivo.endswith('.csv')]
    
    # Si no se encuentran archivos, lanzar un error
    if len(archivos_csv) == 0:
        raise ValueError("No se encontraron archivos CSV que comiencen con 'Mitula'. Verifica la ruta y los archivos.")
    
    # Imprimir los archivos encontrados
    print("Archivos CSV encontrados:")
    for archivo in archivos_csv:
        print(archivo)
    
    # Cargar y concatenar los datos de los archivos CSV
    datos = pd.concat([pd.read_csv(archivo, delimiter='|') for archivo in archivos_csv], ignore_index=True)
    
    return datos

# Cargar los datos
df_mitula = cargar_datos_mitula()

# Análisis del tipo de datos en cada columna
print("\nAnálisis de tipos de datos:")
print(df_mitula.info())


# 1. Distribución del Precio de las Propiedades - Gráfico de KDE con línea de valor medio
plt.figure(figsize=(10, 6))
sns.kdeplot(df_mitula['Precio'], fill=True, color="b", bw_adjust=0.5)
plt.axvline(df_mitula['Precio'].mean(), color='red', linestyle='--', label=f'Media: {df_mitula["Precio"].mean():,.0f} USD')
plt.title('Distribución del Precio de las Propiedades')
plt.xlabel('Precio')
plt.ylabel('Densidad')
plt.legend()
plt.savefig('images/Mitula/Mitula_exploratorio_precio.png')
plt.show()


# 2. Distribución de Áreas (m²) - Histograma con Línea de Densidad
plt.figure(figsize=(10, 6))
sns.histplot(df_mitula['Área (m²)'], kde=True, color="skyblue", bins=20)
plt.title('Distribución del Área (m²) - Histograma con Línea de Densidad')
plt.xlabel('Área (m²)')
plt.ylabel('Frecuencia')
plt.savefig('images/Mitula/Mitula_exploratorio_area.png')
plt.show()


# 3. Relación entre Precio y Área - Gráfico de Dispersión con Colores
plt.figure(figsize=(10, 6))
scatter = plt.scatter(x=df_mitula['Área (m²)'], y=df_mitula['Precio'], 
                      c=df_mitula['Precio'], s=df_mitula['Habitaciones']*30, cmap="coolwarm", alpha=0.6, edgecolor='k')
plt.title('Relación entre Precio y Área')
plt.xlabel('Área (m²)')
plt.ylabel('Precio (USD)')
plt.colorbar(scatter, label='Precio')
plt.savefig('images/Mitula/Mitula_exploratorio_precio_vs_area.png')
plt.show()


# 4. Análisis de Distribución del Área por Ubicación - Gráfico Boxplot
plt.figure(figsize=(12, 8))
# Crear boxplot para analizar la distribución del área por ubicación
sns.boxplot(x='Ubicación', y='Área (m²)', data=df_mitula)
plt.title('Distribución del Área por Ubicación - Boxplot')
plt.xlabel('Ubicación')
plt.ylabel('Área (m²)')
plt.xticks(rotation=90)
plt.grid(True)
# Guardar el gráfico
plt.savefig('images/Mitula/Mitula_exploratorio_area_ubicacion_boxplot.png')
plt.show()




# 5. Instalaciones más Comunes - Gráfico de Barras con Colores Diferentes
plt.figure(figsize=(10, 6))
instalaciones_separadas = df_mitula['Instalaciones'].str.get_dummies(sep=', ').sum().sort_values(ascending=False)
sns.barplot(x=instalaciones_separadas.values, y=instalaciones_separadas.index, color="blue")
plt.title('Instalaciones más Comunes')
plt.xlabel('Frecuencia')
plt.ylabel('Instalación')
plt.savefig('images/Mitula/Mitula_exploratorio_instalaciones.png')
plt.show()


# 6. Agencias con Más Propiedades - Gráfico de Tarta (Pastel)
plt.figure(figsize=(12, 8))
agencias = df_mitula['Nombre de la agencia'].value_counts().reset_index()
agencias.columns = ['Nombre de la agencia', 'Conteo']
# Crear un gráfico de pastel
plt.pie(agencias['Conteo'], labels=agencias['Nombre de la agencia'], autopct='%1.1f%%', colors=sns.color_palette("pastel"))
plt.title('Agencias con Más Propiedades - Gráfico de Tarta')
plt.savefig('images/Mitula/Mitula_exploratorio_agencias_tarta.png')
plt.show()


# 7. Relación entre Ubicación y Precio Promedio - Gráfico de Barras Simplificado
plt.figure(figsize=(10, 6))
ubicacion_precio = df_mitula.groupby('Ubicación')['Precio'].mean().reset_index().sort_values('Precio', ascending=False)
# Usar un color fijo sin palette
sns.barplot(x='Precio', y='Ubicación', data=ubicacion_precio, color="blue")
plt.title('Relación entre Ubicación y Precio Promedio')
plt.xlabel('Precio Promedio')
plt.ylabel('Ubicación')
plt.savefig('images/Mitula/Mitula_exploratorio_precio_ubicacion.png')
plt.show()


# 8. Relación entre Número de Instalaciones y Precio - Gráfico de Dispersión
plt.figure(figsize=(10, 6))
# Crear una nueva columna que cuente el número de instalaciones
df_mitula['Cantidad de Instalaciones'] = df_mitula['Instalaciones'].apply(lambda x: len(str(x).split(', ')) if pd.notnull(x) else 0)
# Gráfico de dispersión para analizar la relación entre el número de instalaciones y el precio
scatter = plt.scatter(x=df_mitula['Cantidad de Instalaciones'], y=df_mitula['Precio'], 
                      c=df_mitula['Precio'], s=df_mitula['Área (m²)'], cmap="coolwarm", alpha=0.6, edgecolor='k')
# Añadir etiquetas y título
plt.title('Relación entre el Número de Instalaciones y el Precio')
plt.xlabel('Cantidad de Instalaciones')
plt.ylabel('Precio (USD)')
plt.colorbar(scatter, label='Precio (USD)')
# Guardar el gráfico
plt.savefig('images/Mitula/Mitula_exploratorio_instalaciones_vs_precio.png')
plt.show()



# 9. Segmentación de Precios por Número de Habitaciones - Boxplot
plt.figure(figsize=(12, 8))
# Crear boxplot con una paleta simple sin hue
sns.boxplot(x='Habitaciones', y='Precio', data=df_mitula)
plt.title('Segmentación de Precios por Número de Habitaciones - Boxplot')
plt.xlabel('Número de Habitaciones')
plt.ylabel('Precio (USD)')
plt.grid(True)
# Guardar el gráfico
plt.savefig('images/Mitula/Mitula_exploratorio_precio_habitaciones_boxplot.png')
plt.show()


# 10. Análisis de Correlación entre Variables - Mapa de Calor
plt.figure(figsize=(10, 6))
# Seleccionamos solo las columnas numéricas
df_numerico = df_mitula[['Precio', 'Área (m²)', 'Habitaciones', 'Baños']]
# Calcular la matriz de correlación
matriz_correlacion = df_numerico.corr()
# Crear un mapa de calor
sns.heatmap(matriz_correlacion, annot=True, cmap='coolwarm', linewidths=0.5, fmt='.2f')
plt.title('Mapa de Calor de Correlación entre Variables Numéricas')
plt.savefig('images/Mitula/Mitula_exploratorio_mapa_calor.png')
plt.show()
