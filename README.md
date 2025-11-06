# Proyecto 2: Pipeline ETL de Datos Financieros

Este proyecto demuestra la creación de un pipeline ETL (Extract, Transform, Load) completo y automatizado. El script de Python extrae datos diarios de precios de acciones desde la API de Alpha Vantage, los transforma usando Pandas y los carga en una base de datos MySQL para su posterior análisis.

## ⚙️ Tecnologías Utilizadas

* **Python 3**
* **API:** Alpha Vantage (para datos bursátiles).
* **Base de Datos:** MySQL
* **Librerías Clave:**
    * `requests`: Para realizar las llamadas a la API.
    * `pandas`: Para la limpieza, transformación y manipulación de los datos.
    * `SQLAlchemy`: Para crear la conexión con la base de datos MySQL.
    * `PyMySQL`: Como el "conector" o "driver" entre SQLAlchemy y MySQL.
    * `python-dotenv`: Para la gestión segura de credenciales (API Key y contraseñas de BD).

## 🔄 El Pipeline ETL

El script `etl_finanzas.py` ejecuta el proceso completo en tres fases:

### 1. Extract (Extracción)
* Se conecta de forma segura a la API de Alpha Vantage (usando una API Key cargada desde un archivo `.env`).
* Extrae los datos de `TIME_SERIES_DAILY` para un símbolo bursátil específico (ej. 'AAPL').
* Recibe los datos en formato JSON crudo.

### 2. Transform (Transformación)
* Convierte la respuesta JSON en un DataFrame de Pandas.
* Limpia y estandariza los nombres de las columnas (ej. `1. open` -> `open`).
* Convierte los tipos de datos de texto a numéricos (`float`) y fechas (`datetime`).
* Añade el símbolo (ej. 'AAPL') como una columna para poder rastrear múltiples acciones a futuro.

### 3. Load (Carga)
* Establece una conexión segura con la base de datos MySQL (cargando credenciales desde `.env`).
* Maneja caracteres especiales en las contraseñas (como `@`) usando `urllib.parse.quote_plus`.
* Carga el DataFrame transformado en la tabla `precios_diarios`.
* Usa `if_exists='append'`, permitiendo que el script se ejecute diariamente para añadir nuevos datos sin borrar los antiguos.

## 🚀 Cómo Ejecutar

1.  Clonar este repositorio: `git clone ...`
2.  Navegar a la carpeta del proyecto.
3.  Crear un entorno virtual (recomendado) e instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crear un archivo `.env` (ver `env.example`) y añadir las credenciales:
    ```ini
    API_KEY=TU_API_KEY_DE_ALPHAVANTAGE
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=tu_contraseña_mysql
    DB_NAME=finanzas_db
    ```
5.  Asegurarse de que el servicio de MySQL esté corriendo y la base de datos `finanzas_db` exista.
6.  Ejecutar el pipeline:
    ```bash
    python etl_finanzas.py
    ```

    ---

## Proyecto 3: Dashboard de BI con Power BI

Como paso final del pipeline, los datos limpios almacenados en la base de datos MySQL (`finanzas_db`) se conectan a Power BI para crear un dashboard de análisis financiero.

Este informe interactivo muestra la tendencia de precios (Gráfico de Velas con SMA de 20 días), el volumen de negociación y los KPIs clave (Último precio, Máximos/Mínimos y Volumen Promedio), permitiendo un análisis en tiempo real.

**[¡Haz clic aquí para ver el dashboard interactivo en la web!](https://app.powerbi.com/groups/me/reports/7c2d9c4d-a54a-42b6-ad7d-919dc332952e/0d52565da6402f184855?experience=power-bi)**

### Vista Previa del Dashboard

[![Vista Previa del Dashboard](dashboard_preview.png)](https://app.powerbi.com/groups/me/reports/7c2d9c4d-a54a-42b6-ad7d-919dc332952e/0d52565da6402f184855?experience=power-bi)