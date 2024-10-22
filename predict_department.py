# predict_department.py
import pandas as pd
import numpy as np
import re
import joblib
from nltk import download
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split  # Add this import
from sklearn.svm import SVC

# Download necessary NLTK resources
download('punkt')
download('stopwords')
download('wordnet')

# Function to clean and preprocess text
def clean_and_preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)

# Load the dataset
data = pd.read_csv('DATA_BASE/SYMPTOMS_MAPPING_TO_DEPARTMENT.csv')
data['text'] = data['text'].apply(clean_and_preprocess_text)

# Train the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.85)
X = tfidf_vectorizer.fit_transform(data['text'])

# Save the vectorizer for later use
joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.pkl')

# Vectorize the text data
y = data['Department']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the SVM model with probability estimation
svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X_train, y_train)

# Save the trained model
joblib.dump(svm_model, 'svm_model.pkl')

# Function to predict the department with a confidence check
def predict_department(symptom_text):
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    model = joblib.load('svm_model.pkl')
    
    processed_text = clean_and_preprocess_text(symptom_text)
    symptom_features = vectorizer.transform([processed_text])
    probabilities = model.predict_proba(symptom_features)[0]
    max_probability = np.max(probabilities)
    
    # Set a probability threshold
    threshold = 0.5  # Adjust based on your model validation

    if max_probability < threshold:
        return "General"
    else:
        return model.predict(symptom_features)[0]
