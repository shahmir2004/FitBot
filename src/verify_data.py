import json
import os

def load_training_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, '../data/training_data.json')
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Error: training_data.json not found.")
        return []

if __name__ == "__main__":
    data = load_training_data()
    print(f"Loaded {len(data)} training examples.")
    
    # Count intents to ensure balance
    intent_counts = {}
    for item in data:
        intent = item['intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    print("\n--- Intent Distribution ---")
    for intent, count in intent_counts.items():
        print(f"{intent}: {count} examples")