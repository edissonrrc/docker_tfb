import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

# Función para entrenar el modelo de predicción del precio
def train_price_model(df):
    X = df[['habitaciones', 'superficie', 'aseos', 'zona', 'extras']]
    y = df['precio']
    
    # Convertir zona y extras en variables dummies
    X = pd.get_dummies(X, columns=['zona', 'extras'], drop_first=True)

    # Entrenar el modelo de precio
    price_model = RandomForestRegressor()
    price_model.fit(X, y)

    return price_model, X.columns  # Retornar también las columnas para referencia futura

# Función para entrenar el modelo de predicción de agencia, zona y otras características
def train_other_models(df):
    classifiers = {}
    
    # Definir qué características son categóricas y cuáles son continuas
    categorical_features = ['agencia', 'zona', 'extras']
    continuous_features = ['aseos', 'superficie', 'gastos']

    for feature in categorical_features:
        X = df[['precio', 'habitaciones']]
        y = df[feature]
        
        # Convertir zona y extras a variables dummies si es necesario
        X = pd.get_dummies(X, drop_first=True)

        # Entrenar un clasificador para las variables categóricas
        clf = RandomForestClassifier()
        clf.fit(X, y)
        
        classifiers[feature] = clf

    for feature in continuous_features:
        X = df[['precio', 'habitaciones']]
        y = df[feature]
        
        # Entrenar un regresor para las variables continuas
        reg = RandomForestRegressor()
        reg.fit(X, y)
        
        classifiers[feature] = reg

    return classifiers

# Función para hacer predicción de precio y agencia
def predict_price_agency(price_model, feature_columns, classifiers, habitaciones, superficie, aseos, zona, extras):
    # Asignar valores predeterminados si el usuario deja campos vacíos
    if not zona:
        zona = 'Quito'  # Valor por defecto para zona
    if not extras:
        extras = ''  # Valor por defecto para extras

    # Preprocesar los datos de entrada
    input_data = pd.DataFrame([[habitaciones, superficie, aseos, zona, extras]], 
                              columns=['habitaciones', 'superficie', 'aseos', 'zona', 'extras'])

    # Convertir zona y extras en variables dummies
    input_data = pd.get_dummies(input_data, columns=['zona', 'extras'], drop_first=True)

    # Identificar las columnas faltantes y crear un DataFrame con esas columnas llenas de ceros
    missing_columns = list(set(feature_columns) - set(input_data.columns))  # Convertir a lista
    missing_df = pd.DataFrame(0, index=input_data.index, columns=missing_columns)

    # Concatenar las columnas faltantes con el DataFrame original de forma eficiente
    input_data = pd.concat([input_data, missing_df], axis=1)

    # Reordenar las columnas para que coincidan con el modelo
    input_data = input_data[feature_columns]

    # Realizar la predicción del precio
    predicted_price = price_model.predict(input_data)

    # Predecir la agencia más frecuente en esa zona usando las características correctas
    agency_data = pd.DataFrame([[predicted_price[0], habitaciones]], columns=['precio', 'habitaciones'])
    predicted_agency = classifiers['agencia'].predict(agency_data)

    return int(predicted_price[0]), predicted_agency[0]

# Función para predecir las demás características a partir del precio y habitaciones
def predict_features(classifiers, precio, habitaciones):
    # Realizar predicciones para las otras características
    predicciones = {}
    
    feature_data = pd.DataFrame([[precio, habitaciones]], columns=['precio', 'habitaciones'])

    for feature, clf in classifiers.items():
        predicciones[feature] = clf.predict(feature_data)[0]
        # Convertir a entero, excepto aseos que debe tener un decimal
        if feature != 'aseos':
            predicciones[feature] = int(predicciones[feature])
        else:
            predicciones[feature] = round(predicciones[feature], 1)

    return predicciones

# Función para mostrar de manera legible una propiedad
def mostrar_propiedad(propiedad):
    print(f"Captura: {propiedad['captura']}")
    print(f"Precio: ${int(propiedad['precio'])}")
    print(f"Agencia: {propiedad['agencia']}")
    print(f"Baños: {round(propiedad['aseos'], 1)}")
    print(f"Zona: {propiedad['zona']}")
    print(f"Superficie: {int(propiedad['superficie'])} m²")
    print(f"Habitaciones: {int(propiedad['habitaciones'])}")
    print(f"Gastos: ${int(propiedad['gastos'])}")
    print(f"Extras: {propiedad['extras']}")
    print("-" * 40)

# Función para mostrar las dos propiedades más cercanas al precio
def show_closest_properties(df, precio, habitaciones):
    # Filtrar las propiedades por el número de habitaciones aproximado
    propiedades_cercanas = df[(df['habitaciones'] == habitaciones)]

    # Ordenar las propiedades por cercanía al precio ingresado
    propiedades_cercanas = propiedades_cercanas.iloc[(propiedades_cercanas['precio'] - precio).abs().argsort()]

    # Mostrar las dos propiedades más cercanas
    if propiedades_cercanas.shape[0] >= 2:
        print("\nLas dos propiedades más cercanas a lo que buscas son:")
        mostrar_propiedad(propiedades_cercanas.iloc[0])
        mostrar_propiedad(propiedades_cercanas.iloc[1])
    else:
        print("\nNo se encontraron suficientes propiedades cercanas a tus criterios.")

# Función para el estudio de un barrio
def analyze_barrio(df, zona):
    # Filtrar las propiedades por la zona especificada
    propiedades_zona = df[df['zona'] == zona]

    if propiedades_zona.empty:
        print(f"No se encontraron propiedades en la zona: {zona}")
        return

    # Obtener las propiedades con el precio máximo, mínimo y más cercano a la media
    precio_maximo = propiedades_zona.loc[propiedades_zona['precio'].idxmax()]
    precio_minimo = propiedades_zona.loc[propiedades_zona['precio'].idxmin()]
    precio_medio = propiedades_zona.iloc[(propiedades_zona['precio'] - propiedades_zona['precio'].mean()).abs().argsort()[:1]]

    print(f"Propiedad con precio máximo en {zona}:")
    mostrar_propiedad(precio_maximo)
    print(f"\nPropiedad con precio mínimo en {zona}:")
    mostrar_propiedad(precio_minimo)
    print(f"\nPropiedad con precio medio en {zona}:")
    mostrar_propiedad(precio_medio.iloc[0])

# Simulación del flujo del script
def main():
    # Cargar los datos de entrenamiento
    df = pd.read_csv('data/csv/datos_limpios.csv')
    
    # Entrenar el modelo de precio y obtener las columnas
    print("Entrenando modelo de predicción de precio...")
    price_model, feature_columns = train_price_model(df)

    # Entrenar los otros modelos
    print("Entrenando modelos para las demás características...")
    classifiers = train_other_models(df)

    while True:
        print("\nPredicciones para Quito, elegir una opción:")
        print("1: Predicción para vendedores")
        print("2: Predicción para compradores")
        print("3: Estadísticas de una zona")
        print("0: Salir")

        opcion = input("Opción: ")

        if opcion == "1":
            # Solicitar datos del cliente para predecir precio y agencia
            habitaciones = input("Ingrese el número de habitaciones: ")
            superficie = input("Superficie en m²: ")
            aseos = input("Número de baños: ")
            zona = input("Zona (Quito, Cumbaya, Distrito Metropolitano Quito): ")
            extras = input("Extras separados por comas (ascensor, jacuzzi): ")

            # Validar que los valores numéricos no estén vacíos y asignar un valor predeterminado
            habitaciones = int(habitaciones) if habitaciones else 1
            superficie = float(superficie) if superficie else 50.0
            aseos = float(aseos) if aseos else 1.0

            # Realizar la predicción
            predicted_price, predicted_agency = predict_price_agency(price_model, feature_columns, classifiers, habitaciones, superficie, aseos, zona, extras)
            
            print(f"La predicción del precio es: ${predicted_price}")
            print(f"Agencia con más presencia: {predicted_agency}")

            # Mostrar las dos propiedades más cercanas al precio predicho
            show_closest_properties(df, predicted_price, habitaciones)

        elif opcion == "2":
            # Solicitar datos del cliente para predecir las otras características
            precio_input = input("Ingrese el precio aproximado(def 70000): ")
            precio = float(precio_input) if precio_input else 70000  # Valor predeterminado si no se ingresa precio

            habitaciones_input = input("Número de habitaciones que desea(def 1): ")
            habitaciones = int(habitaciones_input) if habitaciones_input else 1

            # Mostrar las dos propiedades más cercanas a lo solicitado
            show_closest_properties(df, precio, habitaciones)

        elif opcion == "3":
            # Solicitar la zona al usuario
            zona = input("Ingrese la zona (Quito, Cumbaya, Distrito Metropolitano Quito)")
            analyze_barrio(df, zona)

        elif opcion == "0":
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()
