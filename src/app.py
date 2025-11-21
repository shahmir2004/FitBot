import streamlit as st
import time
from nlp_pipeline import NLPEngine
from logic_engine import WorkoutGenerator

# --- PAGE CONFIGURATION (Must be first) ---
st.set_page_config(page_title="FitBot Pro", page_icon="💪", layout="centered")

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Chat Input Styling */
    .stTextInput input {
        color: #ffffff;
        background-color: #262730;
        border-radius: 20px;
        border: 1px solid #4e4e4e;
    }
    
    /* Card Styling for Workout Plan */
    .workout-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
        border-left: 5px solid #00c853;
    }
    
    .exercise-item {
        background-color: #374151;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        display: flex;
        justify_content: space-between;
    }
    
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    .highlight {
        color: #00c853;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE ENGINES ---
@st.cache_resource
def load_engines():
    nlp = NLPEngine()
    nlp.train() # Train on startup
    logic = WorkoutGenerator()
    return nlp, logic

nlp_bot, logic_bot = load_engines()

# --- SESSION STATE MANAGEMENT ---
# This keeps memory of the conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm FitBot. I can design a custom workout for you. Tell me your goal (e.g., lose weight, build muscle) to get started!"}
    ]

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "goal": None,
        "equipment": None,
        "injury": None,
        "experience": "beginner"
    }

# --- HELPER FUNCTION: DIALOGUE MANAGER ---
def determine_response(user_text):
    # 1. Understand User
    analysis = nlp_bot.process(user_text)
    intent = analysis['intent']
    entities = analysis['entities']
    
    # 2. Update Context/Memory
    if "GOAL" in entities:
        st.session_state.user_profile['goal'] = entities['GOAL']
    if "EQUIPMENT" in entities:
        st.session_state.user_profile['equipment'] = entities['EQUIPMENT']
    if "INJURY" in entities:
        st.session_state.user_profile['injury'] = entities['INJURY']
    if "EXPERIENCE" in entities:
        st.session_state.user_profile['experience'] = entities['EXPERIENCE']

    # 3. Decide Next Step (State Machine)
    profile = st.session_state.user_profile
    
    # Scenario A: User wants to reset/restart
    if intent == "greeting":
        return "Hey there! Ready to work out? Tell me your main fitness goal."
        
    # Scenario B: Missing Goal
    if not profile['goal']:
        return "I can help with that. First, what is your primary goal? (e.g., Muscle Gain, Fat Loss)"
    
    # Scenario C: Missing Equipment (Assume 'none' if not stated, but asking is better for UX)
    if not profile['equipment']:
        return f"Got it, we are focusing on **{profile['goal']}**. What equipment do you have access to? (e.g., Dumbbells, Gym, or just Bodyweight)"
        
    # Scenario D: Ready to Generate
    # If we have Goal + Equipment, we can generate (Injury/Exp are optional/defaulted)
    if intent == "request_workout" or (profile['goal'] and profile['equipment']):
        
        # Generate Plan
        plan = logic_bot.generate_workout(profile)
        
        # Format the Output nicely using HTML/Markdown
        response_md = f"""
        <div class="workout-card">
            <h3>🏋️ Custom {plan['goal'].title()} Plan</h3>
            <p><strong>Equipment:</strong> {profile['equipment'].title()} <br>
            <strong>Focus:</strong> {profile['experience'].title()}</p>
            <hr style="border-color: #4b5563;">
        """
        
        for ex in plan['routine']:
            response_md += f"""
            <div class="exercise-item">
                <span><strong>{ex['exercise']}</strong></span>
                <span class="highlight">{ex['sets']} x {ex['reps']}</span>
            </div>
            <div style="font-size: 0.8em; color: #9ca3af; margin-bottom: 10px;">
                Rest: {ex['rest']} | Note: {ex['notes']}
            </div>
            """
        
        response_md += "</div>"
        
        # Clear state to allow new workout generation next time (optional)
        # st.session_state.user_profile['goal'] = None 
        
        return response_md

    return "I'm listening. Tell me more about your fitness goals or equipment."

# --- MAIN UI LAYOUT ---

st.title("FitBot Pro 💪")
st.markdown("Your AI Personal Trainer")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(message["content"], unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

# Chat Input Area
if prompt := st.chat_input("Type here (e.g., 'I have dumbbells and want to build muscle')"):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Bot Response (with Loading effect)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(0.5) # Simulate processing time for realism
            response = determine_response(prompt)
            st.markdown(response, unsafe_allow_html=True)
            
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- SIDEBAR FOR DEBUGGING/INFO ---
with st.sidebar:
    st.header("Current Context")
    st.write("The bot currently knows this about you:")
    st.json(st.session_state.user_profile)
    
    if st.button("Reset Conversation"):
        st.session_state.user_profile = {"goal": None, "equipment": None, "injury": None, "experience": "beginner"}
        st.session_state.messages = [{"role": "assistant", "content": "Conversation reset. What is your goal?"}]
        st.rerun()