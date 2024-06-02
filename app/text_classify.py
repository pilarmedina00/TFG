from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

tokenizer = DistilBertTokenizer.from_pretrained("lxyuan/distilbert-base-multilingual-cased-sentiments-student")
model = DistilBertForSequenceClassification.from_pretrained("lxyuan/distilbert-base-multilingual-cased-sentiments-student")

label_mapping = {
    0: 'positive',
    1: 'neutral',
    2: 'negative'
}

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    predicted_label_id = outputs.logits.argmax().item()
    sentiment = label_mapping[predicted_label_id]
    return sentiment
