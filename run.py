from app import create_app
from app.data_collect import collect_and_store_data

# Especifica el tópico de interés
TOPIC = "Machismo"

# Definir configuraciones para la conexión a MongoDB
API_KEY = "AIzaSyBqXIfVxCWijPUIUl0JmdwfvqdWXhoYrMw"
MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "youtube_db"
COLLECTION_NAME = "videos"
WORDS_COLLECTION = "palabras_comunes"

# Recolectar y almacenar datos
collect_and_store_data(TOPIC, API_KEY, MONGODB_URI, DB_NAME, COLLECTION_NAME, WORDS_COLLECTION)

# Crear la aplicación Flask
app = create_app()

# Ejecutar el servidor Flask
if __name__ == "__main__":
    app.run(debug=False)
