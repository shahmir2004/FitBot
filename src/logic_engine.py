import json
import os
import random

class WorkoutGenerator:
    def __init__(self):
        self.exercises = self._load_exercises()
        
        # Define logic for sets/reps based on goals
        self.goal_params = {
            "strength": {"sets": 5, "reps": "5", "rest": "3 min"},
            "hypertrophy": {"sets": 3, "reps": "10-12", "rest": "90 sec"},
            "muscle gain": {"sets": 3, "reps": "10-12", "rest": "90 sec"},
            "fat loss": {"sets": 4, "reps": "15-20", "rest": "45 sec"},
            "endurance": {"sets": 4, "reps": "15-20", "rest": "45 sec"},
            "general fitness": {"sets": 3, "reps": "12-15", "rest": "60 sec"}
        }

    def _load_exercises(self):
        """Internal method to load the JSON database"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, '../data/exercises.json')
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def generate_workout(self, user_profile):
        """
        Main logic function.
        user_profile expects keys: ['goal', 'equipment', 'experience', 'injury']
        """
        valid_exercises = []
        
        # Normalize inputs
        user_goal = (user_profile.get('goal') or 'general fitness').lower()
        user_equip = (user_profile.get('equipment') or 'bodyweight').lower()
        user_injury = (user_profile.get('injury') or '').lower()
        user_exp = (user_profile.get('experience') or 'beginner').lower()

        # 1. FILTRATION LOGIC
        for ex in self.exercises:
            # A. Check Equipment (If user has dumbbells, they can also do bodyweight)
            allowed_equip = ['bodyweight']
            if 'dumbbell' in user_equip:
                allowed_equip.append('dumbbells')
            if 'barbell' in user_equip:
                allowed_equip.append('barbell')
            
            # Check if exercise requires equipment user has
            # logic: intersection of exercise equipment and user's allowed list
            ex_equip_lower = [e.lower() for e in ex['equipment']]
            if not any(item in allowed_equip for item in ex_equip_lower):
                continue # Skip this exercise

            # B. Check Injury (Safety Rule)
            if user_injury:
                # Check if user's injury is in the contraindications list
                # We use partial matching (e.g. "knee" matches "severe knee pain")
                contraindications = [c.lower() for c in ex.get('contraindications', [])]
                if any(user_injury in c for c in contraindications):
                    continue # Skip unsafe exercise

            # C. Check Difficulty (Beginners shouldn't do Advanced moves)
            if user_exp == 'beginner' and ex['difficulty'].lower() == 'advanced':
                continue

            valid_exercises.append(ex)

        # 2. SELECTION LOGIC
        # Prioritize exercises that match the specific goal
        primary_picks = [ex for ex in valid_exercises if any(user_goal in g.lower() for g in ex['primary_goals'])]
        secondary_picks = [ex for ex in valid_exercises if ex not in primary_picks]

        # Build the routine (Mix of Primary and Secondary)
        workout_plan = []
        
        # Try to get 3 primary exercises + 2 secondary exercises
        if len(primary_picks) >= 3:
            workout_plan.extend(random.sample(primary_picks, 3))
        else:
            workout_plan.extend(primary_picks)
            
        needed = 5 - len(workout_plan)
        if len(secondary_picks) >= needed:
            workout_plan.extend(random.sample(secondary_picks, needed))
        else:
            workout_plan.extend(secondary_picks)

        # 3. FORMATTING LOGIC (Apply Sets/Reps)
        params = self.goal_params.get(user_goal, self.goal_params['general fitness'])
        
        formatted_plan = {
            "goal": user_goal,
            "routine": []
        }

        for ex in workout_plan:
            formatted_plan["routine"].append({
                "exercise": ex['name'],
                "sets": params['sets'],
                "reps": params['reps'],
                "rest": params['rest'],
                "notes": f"Focus on form. {ex['difficulty']} level."
            })

        return formatted_plan

# --- Testing Block ---
if __name__ == "__main__":
    engine = WorkoutGenerator()
    
    # Test Case 1: Beginner with no equipment wanting to lose fat
    profile1 = {
        "goal": "fat loss",
        "equipment": "none",
        "experience": "beginner",
        "injury": "none"
    }
    
    # Test Case 2: Intermediate with Dumbbells but Knee Pain
    profile2 = {
        "goal": "hypertrophy",
        "equipment": "dumbbells",
        "experience": "intermediate",
        "injury": "knee" 
    }

    print("--- Plan 1 (Fat Loss, Bodyweight) ---")
    print(json.dumps(engine.generate_workout(profile1), indent=2))

    print("\n--- Plan 2 (Muscle, Dumbbells, NO KNEE EXERCISES) ---")
    print(json.dumps(engine.generate_workout(profile2), indent=2))