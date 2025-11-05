import requests
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine # <--- [NUEVO] Importamos SQLAlchemy
from urllib.parse import quote_plus

# --- Cargar Variables de Entorno ---
load_dotenv()
API_KEY = os.getenv('API_KEY')

# [NUEVO] Cargar credenciales de BD
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Validar que todas las variables de entorno existan
if not all([API_KEY, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    print("Error: Faltan variables de entorno. Revisa tu archivo .env")
    exit()


# --- (E)XTRACT ---
def extraer_datos_acciones(simbolo):
    print(f"Iniciando extracción para el símbolo: {simbolo}...")
    params = {'function': 'TIME_SERIES_DAILY', 'symbol': simbolo, 'apikey': API_KEY, 'outputsize': 'compact'}
    url = 'https://www.alphavantage.co/query'
    try:
        respuesta = requests.get(url, params=params)
        respuesta.raise_for_status() 
        datos_json = respuesta.json()
        print("Extracción exitosa.")
        return datos_json
    except Exception as e:
        print(f"Error al llamar a la API: {e}")
        return None

# --- (T)RANSFORM ---
def transformar_datos(datos_json, simbolo):
    print(f"Iniciando transformación para {simbolo}...")
    try:
        datos_series = datos_json['Time Series (Daily)']
    except KeyError:
        print("Error: 'Time Series (Daily)' no se encontró en el JSON.")
        print("Respuesta de la API:", datos_json)
        return None

    df = pd.DataFrame.from_dict(datos_series, orient='index')
    nombres_nuevos = {
        '1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'
    }
    df.rename(columns=nombres_nuevos, inplace=True)
    
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df.index = pd.to_datetime(df.index)
    df['symbol'] = simbolo
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    df = df[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
    print("Transformación exitosa.")
    return df

# --- [NUEVA FUNCIÓN (L)OAD] ---
def cargar_datos_sql(df):
    """
    Carga el DataFrame limpio en la base de datos MySQL.
    """
    print("Iniciando carga a MySQL...")
    
    try:# "Escapamos" la contraseña para caracteres especiales como '@'
        password_esc = quote_plus(DB_PASSWORD)
        # 1. Crear la "cadena de conexión"
        # Formato: mysql+mysqlclient://usuario:contraseña@host/base_de_datos
        # Formato: mysql+pymysql://usuario:contraseña@host/base_de_datos
        cadena_conexion = f"mysql+pymysql://{DB_USER}:{password_esc}@{DB_HOST}/{DB_NAME}"
        # 2. Crear el "motor" de SQLAlchemy
        engine = create_engine(cadena_conexion)
        
        # 3. Cargar el DataFrame en la tabla SQL
        # 'precios_diarios' será el nombre de nuestra tabla
        # if_exists='append': Si la tabla existe, añade los datos.
        # index=False: No guardar el índice de pandas (0, 1, 2...) en la BD
        df.to_sql('precios_diarios', con=engine, if_exists='append', index=False)
        
        print(f"¡Carga exitosa! {len(df)} filas añadidas a la tabla 'precios_diarios' en '{DB_NAME}'.")
    
    except Exception as e:
        print(f"Error al cargar datos en MySQL: {e}")


# --- [BLOQUE PRINCIPAL MODIFICADO] ---
if __name__ == "__main__":
    
    simbolo_accion = 'AAPL' 
    datos_crudos = extraer_datos_acciones(simbolo_accion)
    
    if datos_crudos:
        if "Error Message" in datos_crudos:
            print(f"Error de la API: {datos_crudos['Error Message']}")
        elif "Information" in datos_crudos:
             print(f"Información de la API (límite de llamadas): {datos_crudos['Information']}")
        else:
            df_limpio = transformar_datos(datos_crudos, simbolo_accion)
            
            if df_limpio is not None:
                print("\n--- Datos Transformados (DataFrame) ---")
                print(df_limpio.head())
                print("---------------------------------------")
                
                # --- [NUEVO] Llamamos a la función de carga ---
                cargar_datos_sql(df_limpio)