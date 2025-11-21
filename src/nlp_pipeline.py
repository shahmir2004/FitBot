import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline

class NLPEngine:
    def __init__(self):
        self.model = None
        self.is_trained = False
        
        # Define simple keywords for entity extraction (Rule-based NER)
        # In a large production system, we would use Spacy NER, but for a project 
        # with small data, dictionary matching is more accurate.
        self.entity_keywords = {
            "GOAL": ["lose weight", "fat loss", "muscle gain", "hypertrophy", "strength", "endurance", "get strong", "build muscle"],
            "EQUIPMENT": ["dumbbells", "barbell", "kettlebell", "bodyweight", "gym", "machine", "bench"],
            "EXPERIENCE": ["beginner", "intermediate", "advanced"],
            "INJURY": ["knee pain", "back pain", "shoulder pain", "wrist pain", "bad knees", "bad back"]
        }

    def load_data(self):
        """Loads training data from JSON file"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, '../data/training_data.json')
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def train(self):
        """Trains the Intent Classifier using SVM"""
        training_data = self.load_data()
        
        texts = [item['text'] for item in training_data]
        labels = [item['intent'] for item in training_data]
        
        # Create a pipeline: 
        # 1. TF-IDF (converts words to numbers)
        # 2. LinearSVC (Support Vector Machine classifier)
        self.model = make_pipeline(TfidfVectorizer(), LinearSVC())
        self.model.fit(texts, labels)
        self.is_trained = True
        print("NLP Engine Trained Successfully.")

    def extract_entities(self, text):
        """Rule-based Entity Recognition"""
        found_entities = {}
        text_lower = text.lower()
        
        for label, keywords in self.entity_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_entities[label] = keyword
                    # We break to avoid capturing substrings (simple logic)
                    break 
        return found_entities

    def process(self, user_input):
        """Main function: Predicts Intent and Extracts Entities"""
        if not self.is_trained:
            raise Exception("Model not trained! Call train() first.")
        
        # 1. Predict Intent
        intent = self.model.predict([user_input])[0]
        
        # 2. Extract Entities
        entities = self.extract_entities(user_input)
        
        return {
            "text": user_input,
            "intent": intent,
            "entities": entities
        }

# --- Testing Block ---
if __name__ == "__main__":
    bot = NLPEngine()
    bot.train()
    
    # Test Sentences
    test_sentences = [
        "Hello there",
        "I want to build muscle",
        "I have a pair of dumbbells",
        "Hello friend",
        "I have bad knees",
        "Please give me a workout plan"
    ]
    
    print("\n--- NLP Test Results ---")
    for text in test_sentences:
        result = bot.process(text)
        print(f"Input: '{text}'")
        print(f"  -> Intent: {result['intent']}")
        print(f"  -> Entities: {result['entities']}")
        print("-" * 30)