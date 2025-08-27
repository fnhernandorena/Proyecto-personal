# Sincronizador de Transacciones de Amazon SP-API
Este script se conecta a la API de Vendedores de Amazon (SP-API) para descargar las transacciones financieras, guardarlas en una base de datos PostgreSQL y mostrar un resumen de ventas por SKU.

## ¿Cómo Funciona? 🧑‍💻
El proceso es muy simple y se divide en tres pasos automáticos:

Conexión y Descarga: El script se comunica de forma segura con Amazon para pedirle un listado de todos los eventos financieros recientes (ventas, devoluciones, etc.).

Guardado y Limpieza: Guarda cada uno de estos eventos en una base de datos PostgreSQL. Está diseñado para evitar guardar información duplicada si se ejecuta varias veces.

Resumen Final: Una vez guardado todo, consulta la base de datos y muestra en la pantalla una tabla simple con el total de unidades vendidas y el monto total por cada producto (SKU).

## ¿Cómo Ejecutar el Código? 🚀
Sigue estos pasos para poner en marcha el programa.

### Paso 1: Requisitos Previos
Asegúrate de tener instalados en tu sistema:

Python 3.9 o superior.

PostgreSQL.

### Paso 2: Preparar el Proyecto
Abre una terminal en la carpeta del proyecto.

Crea un entorno virtual para instalar las librerías de forma aislada:

python3 -m venv venv
Activa el entorno virtual:

En Windows:

PowerShell

.\venv\Scripts\activate
En macOS o Linux:

source venv/bin/activate
Instala todas las librerías necesarias con un solo comando:

pip install -r requirements.txt

### Paso 3: Configurar las Credenciales
Crea un archivo llamado .env en la carpeta principal del proyecto.

Copia y pega el siguiente contenido en el archivo .env y reemplaza los valores de ejemplo con tus credenciales reales.

#### --- Base de Datos PostgreSQL ---
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_secreta
DB_HOST=localhost
DB_PORT=5432
DB_NAME=amazon_transactions_db

#### --- Credenciales de Amazon SP-API ---
SP_API_REFRESH_TOKEN=tu_refresh_token_de_amazon
SP_API_CLIENT_ID=tu_client_id_de_lwa
SP_API_CLIENT_SECRET=tu_client_secret_de_lwa
SP_API_LWA_APP_ID=tu_lwa_app_id
SP_API_AWS_SECRET_KEY=tu_aws_secret_key
SP_API_AWS_ACCESS_KEY=tu_aws_access_key
SP_API_ROLE_ARN=arn:aws:iam::xxxxxxxx:role/tu-rol-sp-api
Asegúrate de haber creado una base de datos en PostgreSQL con el nombre que especificaste en DB_NAME.

### Paso 4: ¡Ejecutar!
Con el entorno virtual activado, simplemente ejecuta el script principal:

python main.py

Verás en la terminal los mensajes del proceso y, al finalizar, el resumen de ventas por SKU.