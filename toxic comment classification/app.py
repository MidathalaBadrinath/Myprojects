from flask import Flask, render_template, request, jsonify
import joblib
import re
import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from nltk.corpus import stopwords

# Initialize Flask app
app = Flask(__name__)

# Load the trained model
old_pipeline = joblib.load('model/toxic_comment_classifier.pkl')

# List of toxicity labels
labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']


# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "can not ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub('\W', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = text.strip(' ')
    return text


@app.route('/')
def index():
    return render_template('index.html', labels=labels)  # Pass labels to frontend


@app.route('/predict', methods=['POST'])
def predict():
    # Get the comment from the request
    comment = request.form['comment']
    processed_comment = preprocess_text(comment)

    # Use the model to predict toxicity
    prediction = old_pipeline.predict([processed_comment])[0]

    # Determine the toxicity levels from the prediction
    toxic_labels = [labels[i] for i in range(len(labels)) if prediction[i] == 1]

    return render_template('result.html', comment=comment, toxic_labels=toxic_labels, labels=labels)


@app.route('/update', methods=['POST'])
def update():
    comment = request.form['comment']
    selected_labels = request.form.getlist('labels')  # Get list of selected labels

    # You would have a function to update the dataset and retrain the model
    update_dataset_and_retrain(comment, selected_labels)

    return jsonify({"message": "Dataset updated and model retrained successfully."})


def update_dataset_and_retrain(comment, selected_labels):
    # Add functionality to update dataset and retrain model here
    pass


if __name__ == '__main__':
    app.run(debug=True)
