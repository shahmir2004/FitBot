import json
import os

def load_exercises():
    # Define path to the JSON file
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, '../data/exercises.json')
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Error: exercises.json not found.")
        return []

if __name__ == "__main__":
    exercises = load_exercises()
    print(f"Successfully loaded {len(exercises)} exercises from the Knowledge Base.")
    
    # Test: Filter for 'Beginner' exercises
    print("\n--- Beginner Exercises ---")
    for ex in exercises:
        if ex['difficulty'] == "Beginner":
            print(f"- {ex['name']} ({ex['primary_goals'][0]})")