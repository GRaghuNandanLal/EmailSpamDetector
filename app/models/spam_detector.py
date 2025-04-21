import joblib
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

class SpamDetector:
    def __init__(self):
        """Initialize and train the model if not already trained"""
        # Using TfidfVectorizer instead of CountVectorizer for better results
        self.model = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),  # Include both unigrams and bigrams
                min_df=2,  # Minimum document frequency
                max_df=0.95  # Maximum document frequency
            )),
            ('classifier', MultinomialNB(alpha=0.1))  # Adjusted alpha for better spam detection
        ])
        
        # Common spam keywords and patterns
        self.spam_patterns = [
            'free', 'win', 'winner', 'cash', 'prize', 'urgent', 'offer', 'credit',
            'guarantee', 'instant', 'limited', 'discount', 'congratulations',
            'earn', 'money', 'dollar', '$$$', 'work from home', 'no experience',
            'bitcoin', 'investment', 'loan', 'debt', 'weight loss', 'viagra',
            'casino', 'lottery', 'subscribe'
        ]
        
        try:
            # Try to load the trained model
            self.model = joblib.load('app/models/spam_model.joblib')
        except:
            # If model doesn't exist, train a new one
            self._train_model()
    
    def _train_model(self):
        """Train the model using the spam dataset"""
        # Load the dataset
        df = pd.read_csv('data/spam.csv', encoding='latin-1')
        
        # Add synthetic spam examples
        synthetic_spam = pd.DataFrame({
            'v1': ['spam'] * len(self.spam_patterns),
            'v2': [f"Get {pattern} now!" for pattern in self.spam_patterns]
        })
        df = pd.concat([df, synthetic_spam], ignore_index=True)
        
        # Prepare the data
        X = df['v2'].values  # message text
        y = (df['v1'] == 'spam').astype(int)  # convert 'spam'/'ham' to 1/0
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Save the trained model
        joblib.dump(self.model, 'app/models/spam_model.joblib')
    
    def _check_spam_patterns(self, text):
        """Check for common spam patterns in the text"""
        text_lower = text.lower()
        spam_score = 0
        matched_patterns = []
        
        for pattern in self.spam_patterns:
            if pattern.lower() in text_lower:
                spam_score += 1
                matched_patterns.append(pattern)
        
        return spam_score, matched_patterns
    
    def predict(self, text):
        """
        Predict if the given text is spam using both ML model and pattern matching
        """
        if not text:
            raise ValueError("Empty text provided")
        
        # Get ML model prediction
        prediction = self.model.predict([text])[0]
        proba = self.model.predict_proba([text])[0]
        
        # Check for spam patterns
        spam_score, matched_patterns = self._check_spam_patterns(text)
        
        # Adjust prediction based on spam patterns
        if spam_score >= 2:  # If text contains multiple spam patterns
            prediction = 1
            confidence = min(0.99, proba[1] + (spam_score * 0.1))  # Increase confidence
        else:
            confidence = proba[1] if prediction == 1 else proba[0]
        
        result = {
            'is_spam': bool(prediction),
            'confidence': round(confidence * 100, 2),
            'prediction': 'This is a Spam Email!' if prediction == 1 else 'This is a Ham Email!'
        }
        
        # Add matched patterns to the result if it's spam
        if prediction == 1 and matched_patterns:
            result['spam_indicators'] = matched_patterns
            
        return result 