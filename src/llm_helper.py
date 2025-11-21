import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the .env file
load_dotenv()

class LLMInterface:
    def __init__(self):
        # Retrieve the key securely from the environment
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            print("Error: GROQ_API_KEY not found in environment variables.")
            self.client = None
            return

        try:
            self.client = Groq(api_key=self.api_key)
            # Using the latest stable model
            self.model = "llama-3.3-70b-versatile" 
        except Exception as e:
            print(f"LLM Setup Error: {e}")
            self.client = None

    def chat(self, user_message, system_instruction=None):
        """Standard chat conversation"""
        if not self.client:
            return "⚠️ I am currently offline (API Key missing). Please check your setup."

        messages = []
        
        # Default persona
        default_system = "You are FitBot, an enthusiastic and professional personal trainer. Keep answers concise (under 50 words) and motivating."
        
        messages.append({"role": "system", "content": system_instruction or default_system})
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"I'm having trouble connecting to my brain right now. ({str(e)})"

    def narrate_workout(self, plan_json, user_profile):
        """Takes the raw JSON plan and describes it like a human trainer"""
        if not self.client:
            return "Here is your generated workout plan:"

        prompt = f"""
        I have generated a workout plan for a user. 
        User Profile: Goal={user_profile['goal']}, Equipment={user_profile['equipment']}, Injury={user_profile['injury']}.
        
        Here is the Plan Data:
        {str(plan_json)}
        
        Your task:
        1. Write a short, hype-up introduction (1 sentence).
        2. Briefly explain why this plan fits their goal.
        3. Remind them of safety if they have an injury.
        4. Do NOT list the exercises again.
        """
        
        return self.chat(prompt, system_instruction="You are an expert fitness coach explaining a routine.")