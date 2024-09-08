from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

app = Flask(__name__)

# Configure SQLAlchemy for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1122@localhost/deardiarydb'
db = SQLAlchemy(app)

# Define a Model
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_text = db.Column(db.String(500), nullable=False)
    prediction = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Load the machine learning model
pipe_lr = joblib.load(open("txt_emotion.pkl", "rb"))

# Dictionary mapping emotions to emoji icons
emotion_emoji_dict = {
    "anger": "😡",
    "disgust": "🤢",
    "fear": "😱",
    "happy": "😄",
    "joy": "😊",
    "neutral": "😐",
    "sad": "😢",
    "sadness": "😔",
    "shame": "😳",
    "surprise": "😮"
}

# Function to predict emotion
def predict_emotion(docs):
    results = pipe_lr.predict([docs])
    return results[0]

# Function to get prediction probabilities
def get_prediction_proba(docs):
    results = pipe_lr.predict_proba([docs])
    return results

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    entries = Entry.query.all()  # Fetch all entries from the database

    if request.method == 'POST':
        raw_text = request.form['raw_text']
        prediction = predict_emotion(raw_text)
        probability = get_prediction_proba(raw_text)

        classes = pipe_lr[-1].classes_
        proba_df = pd.DataFrame(probability, columns=classes)
        proba_df_clean = proba_df.T.reset_index()
        proba_df_clean.columns = ["emotions", "probability"]

        # Save entry to database
        new_entry = Entry(raw_text=raw_text, prediction=prediction)
        db.session.add(new_entry)
        db.session.commit()

        return render_template('result.html', 
                               raw_text=raw_text, 
                               prediction=prediction,
                               emoji_icon=emotion_emoji_dict[prediction],
                               max_probability=np.max(probability),
                               proba_df=proba_df_clean.to_dict(orient='records'),
                               predicted_emotion=prediction,
                               entries=entries)  # Pass entries to template

    return render_template('index.html', entries=entries)  # Pass entries to template

if __name__ == '__main__':
    app.run(debug=True)
