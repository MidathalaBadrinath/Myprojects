from flask import Flask, render_template, request
import pandas as pd
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
import nltk

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

# Load the trained model
old_pipeline = joblib.load('model/toxic_comment_classifier.pkl')

# Labels
labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

# Mitigation messages
mitigation_messages = {
    'toxic': "You are using harmful language that could hurt others. Please be mindful of your words.",
    'severe_toxic': "This comment contains severe language that may be considered abusive. Please refrain from using such language.",
    'obscene': "Your comment contains inappropriate language. Please keep the conversation respectful.",
    'threat': "Threatening comments are harmful and inappropriate. Please avoid using such language.",
    'insult': "Your comment contains insulting language. Kindly express yourself respectfully.",
    'identity_hate': "Hate speech towards any identity is unacceptable. Please be respectful to all individuals."
}

# Preprocessing function
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
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip(' ')
    return text

# Update dataset and retrain model
def update_dataset_and_retrain(comment, updated_labels, new_model_path='new_model.pkl', dataset_path='new_train.csv'):
    df = pd.read_csv(dataset_path) if pd.io.common.file_exists(dataset_path) else pd.DataFrame(columns=['id', 'comment_text'] + labels)

    # Prevent duplicate comments
    if comment in df['comment_text'].values:
        return "Comment already exists in the dataset."

    # Add the new comment with appropriate labels
    new_row = {
        'id': str(hash(comment)),
        'comment_text': comment,
        **{label: 1 if label in updated_labels else 0 for label in labels}
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save updated dataset
    df.to_csv(dataset_path, index=False)

    # Retrain the model
    X_train = df['comment_text'].apply(preprocess_text)
    y_train = df[labels]

    updated_pipeline = make_pipeline(TfidfVectorizer(stop_words='english'), OneVsRestClassifier(LogisticRegression(), n_jobs=-1))
    updated_pipeline.fit(X_train, y_train)

    # Save the new model
    joblib.dump(updated_pipeline, new_model_path)
    return "Model retrained successfully."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    comment = request.form['comment']
    processed_comment = preprocess_text(comment)

    # Load appropriate model
    df = pd.read_csv('new_train.csv') if pd.io.common.file_exists('new_train.csv') else pd.DataFrame(columns=['id', 'comment_text'] + labels)
    if comment in df['comment_text'].values:
        pipeline = joblib.load('new_model.pkl')
        model_used = "new"
    else:
        pipeline = old_pipeline
        model_used = "old"

    prediction = pipeline.predict([processed_comment])[0]
    predicted_labels = [labels[i] for i, value in enumerate(prediction) if value == 1]

    # Determine if the comment is toxic or healthy and include mitigation feedback
    if any(prediction):
        toxicity_types = [labels[i] for i in range(len(labels)) if prediction[i] == 1]
        status = "toxic"
        feedback = [mitigation_messages[label] for label in toxicity_types]
    else:
        toxicity_types = []
        status = "healthy"
        feedback = ["Thank you for maintaining a respectful tone."]

    # Pass relevant information to the result template
    return render_template(
        'result.html',
        comment=comment,
        predicted_labels=predicted_labels,
        labels=labels,
        model_used=model_used,
        healthy=not predicted_labels,
        status=status,
        feedback=feedback
    )

@app.route('/update', methods=['POST'])
def update():
    comment = request.form['comment']
    is_correct = request.form['is_correct']
    selected_labels = request.form.getlist('labels') if is_correct == 'no' else request.form.getlist('predicted_labels')

    # Update dataset and retrain model
    message = update_dataset_and_retrain(comment, selected_labels)
    return render_template('update_success.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
