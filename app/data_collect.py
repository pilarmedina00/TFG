from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
from app.text_classify import analyze_sentiment
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string

# Descargar recursos necesarios de NLTK para conteo de palabras
nltk.download('punkt')
nltk.download('stopwords')

# Stopwords en español que se eliminarán en el preprocesamiento del texto
stop_words = set(stopwords.words('spanish'))

# Preprocesar el texto antes del conteo
def preprocess_text(text):
    text = text.lower()  # Convertir todo el texto a minúsculas
    text = text.translate(str.maketrans('', '', string.punctuation))  # Eliminar los signos de puntuación
    words = word_tokenize(text, language='spanish')  # Tokenizar el texto (en español)
    words = [word for word in words if word not in stop_words]  # Eliminar stopwords previamente cargados
    return words

# Contear las palabras de texto preprocesado
def count_words(texts):
    all_words = []
    for text in texts:
        words = preprocess_text(text)
        all_words.extend(words)
    word_counts = Counter(all_words)
    return word_counts

# Contear las palabras más usadas de todos los vídeos
def calculate_global_word_frequencies(mongodb_uri, db_name, video_collection_name, word_collection_name):
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    video_collection = db[video_collection_name]
    word_collection = db[word_collection_name]

    all_texts = []

    for document in video_collection.find():
        for comment in document['comments']:
            all_texts.append(comment['comment'])

    word_counts = count_words(all_texts)
    most_common_words = word_counts.most_common(5)  # Obtener las 5 palabras más comunes

    # Limpiar la colección antes de insertar nuevos datos
    word_collection.delete_many({})  
    
    # Insertar las palabras más comunes globalmente en la colección
    for word, freq in most_common_words:
        word_collection.insert_one({'word': word, 'frequency': freq})

    return most_common_words

# Recabar y almacenar los datos de la API
def collect_and_store_data(topic, api_key, mongodb_uri, db_name, video_collection_name, word_collection_name):
    youtube_service = build('youtube', 'v3', developerKey=api_key)
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    video_collection = db[video_collection_name]
    
    # Limpiar la colección antes de insertar nuevos datos
    video_collection.delete_many({})  

    search_response = youtube_service.search().list(
        q=topic,
        type='video',
        part='id,snippet',
        maxResults=25
    ).execute()

    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_title = search_result['snippet']['title']
        video_description = search_result['snippet']['description']
        video_date = datetime.strptime(search_result['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')

        try:
            # Extraer las estadísticas del vídeo para obtener los likes
            video_details = youtube_service.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            
            video_likes = video_details['items'][0]['statistics'].get('likeCount', 0)

            comments = get_video_comments(youtube_service, video_id)
        except HttpError as e:
            if e.resp.status == 403 and 'commentsDisabled' in str(e):
                print("---------------------")
                print(f"Comentarios deshabilitados para el video ID: {video_id}")
                continue
            else:
                raise e

        classified_comments = []
        for comment in comments:
            sentiment = analyze_sentiment(comment['text'])
            comment_date = datetime.strptime(comment['date'], '%Y-%m-%dT%H:%M:%SZ')
            classified_comments.append({
                'username': comment['username'],
                'comment': comment['text'],
                'sentiment': sentiment,
                'date': comment_date,
                'likes': comment['likes']
            })

        # Contear la palabra más usada en los comentarios de cada video
        video_texts = [comment['comment'] for comment in classified_comments]
        video_word_counts = count_words(video_texts)
        most_common_word = video_word_counts.most_common(1)[0] if video_word_counts else ('', 0)

        video_data = {
            'video_id': video_id,
            'title': video_title,
            'description': video_description,
            'date': video_date,
            'likes': video_likes,
            'comments': classified_comments,
            'most_common_word': {
                'word': most_common_word[0],
                'frequency': most_common_word[1]
            }
        }
        video_collection.insert_one(video_data)

    # Contear y almacenar las palabras más comunes globalmente
    most_common_words = calculate_global_word_frequencies(mongodb_uri, db_name, video_collection_name, word_collection_name)
    print("---------------------")
    print("Palabras más comunes globalmente:")
    for word, freq in most_common_words:
        print(f"{word}: {freq}")

# Recabar los comentarios de cada vídeo
def get_video_comments(service, video_id):
    comments = []

    comment_threads = service.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=25
    ).execute()

    for comment_thread in comment_threads['items']:
        comment_snippet = comment_thread['snippet']['topLevelComment']['snippet']
        comment_text = comment_snippet['textDisplay']
        comment_date = comment_snippet['publishedAt']
        comment_likes = comment_snippet.get('likeCount', 0)
        comment_username = comment_snippet.get('authorDisplayName', 'Anónimo')
        comments.append({
            'username': comment_username,
            'text': comment_text,
            'date': comment_date,
            'likes': comment_likes
        })

    return comments
