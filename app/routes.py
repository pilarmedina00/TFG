from flask import Blueprint, render_template, jsonify, request
from pymongo import MongoClient
from datetime import datetime

main = Blueprint('main', __name__)

# Configurar la conexión a MongoDB
MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "youtube_db"
COLLECTION_NAME = "videos"
WORDS_COLLECTION = "palabras_comunes"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
words_collection = db[WORDS_COLLECTION]

@main.route('/')
def index():    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    videos = []
    comments = []
    sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Filtrar vídeos por fecha de publicación
        videos = list(collection.find({
            "date": {"$gte": start_date, "$lte": end_date}
        }))

        # Filtrar comentarios por fecha de publicación
        comments = list(collection.aggregate([
            {"$unwind": "$comments"},
            {"$match": {"comments.date": {"$gte": start_date, "$lte": end_date}}},
            {"$project": {
                "_id": 0,
                "comment": "$comments.comment",
                "sentiment": "$comments.sentiment",
                "date": "$comments.date",
                "username": "$comments.username",
                "likes": {"$ifNull": ["$comments.likes", 0]}
            }}
        ]))
    else:
        # Si no hay filtro, se muestran las listas completas
        videos = list(collection.find())
        
        comments = list(collection.aggregate([
            {"$unwind": "$comments"},
            {"$project": {
                "_id": 0,
                "comment": "$comments.comment",
                "sentiment": "$comments.sentiment",
                "date": "$comments.date",
                "username": "$comments.username",
                "likes": {"$ifNull": ["$comments.likes", 0]} 
            }}
        ]))
        
    # Contear los sentimientos de comentarios para el pie chart
    for comment in comments:
        sentiment = comment['sentiment']
        sentiments[sentiment] += 1

    return render_template('index.html', videos=videos, comments=comments, sentiments=sentiments)

@main.route('/data')
def get_data():
    videos = collection.find()
    data = []
    for video in videos:
        # Se acorta el título para que no supere los 20 caracteres
        truncated_title = video['title'][:35] + '...' if len(video['title']) > 35 else video['title']
        video_data = {
            'title': truncated_title,
            'comments': [{'comment': comment['comment'], 'sentiment': comment['sentiment']} for comment in video['comments']]
        }
        data.append(video_data)
        
    return jsonify(data)

@main.route('/top_words')
def get_top_words():
    top_words = words_collection.find().sort("frequency", -1).limit(5)
    words_data = [{"word": word["word"], "frequency": word["frequency"]} for word in top_words]

    data = {
        "labels": [word["word"] for word in words_data],
        "frequencies": [word["frequency"] for word in words_data]
    }

    return jsonify(data)
