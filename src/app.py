import streamlit as st
import time
from nlp_pipeline import NLPEngine
from logic_engine import WorkoutGenerator
from llm_helper import LLMInterface # <--- IMPORT NEW MODULE

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FitBot Pro + Llama3", page_icon="🤖", layout="centered")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTextInput input { color: #ffffff; background-color: #262730; border-radius: 20px; }
    .workout-card { background-color: #1f2937; padding: 20px; border-radius: 15px; border-left: 5px solid #00c853; margin-bottom: 15px; }
    .exercise-item { background-color: #374151; padding: 10px; border-radius: 8px; margin: 5px 0; display: flex; justify_content: space-between; }
    .highlight { color: #00c853; font-weight: bold; }
    .ai-commentary { font-style: italic; color: #a7f3d0; border-left: 2px solid #a7f3d0; padding-left: 10px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE ENGINES ---
@st.cache_resource
def load_engines():
    nlp = NLPEngine()
    nlp.train()
    logic = WorkoutGenerator()
    llm = LLMInterface() # <--- Initialize LLM
    return nlp, logic, llm

nlp_bot, logic_bot, llm_bot = load_engines()

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm FitBot (powered by Llama 3). What's your fitness goal today?"}
    ]

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "goal": None, "equipment": None, "injury": "", "experience": "beginner"
    }

# --- MAIN LOGIC ---
def determine_response(user_text):
    # 1. Understand User (NLP Layer)
    analysis = nlp_bot.process(user_text)
    intent = analysis['intent']
    entities = analysis['entities']
    
    # Update Context
    for key, value in entities.items():
        st.session_state.user_profile[key.lower()] = value

    profile = st.session_state.user_profile
    
    # 2. Scenario: Greeting or Reset
    if intent == "greeting":
        return llm_bot.chat(user_text) # Let LLM handle hello/hi

    # 3. Scenario: Generate Workout
    # We check if we have enough info to generate a plan
    if (intent == "request_workout" or (profile['goal'] and profile['equipment'])):
        
        # A. Generate Logic-Based Plan (The Safety Layer)
        plan = logic_bot.generate_workout(profile)
        
        # B. Generate AI Commentary (The Personality Layer)
        ai_intro = llm_bot.narrate_workout(plan, profile)

        # C. Construct UI
        response_md = f"""
        <div class="ai-commentary">💡 {ai_intro}</div>
        <div class="workout-card">
            <h3>🏋️ Custom {plan['goal'].title()} Plan</h3>
            <p style="color: #9ca3af; font-size: 0.9em;">Designed for: {profile['experience'].title()} | Equip: {profile['equipment'].title()}</p>
            <hr style="border-color: #4b5563;">
        """
        
        for ex in plan['routine']:
            response_md += f"""
            <div class="exercise-item">
                <span><strong>{ex['exercise']}</strong></span>
                <span class="highlight">{ex['sets']} x {ex['reps']}</span>
            </div>
            """
        response_md += "</div>"
        
        # Optional: Reset context slightly to allow follow-up questions
        return response_md

    # 4. Scenario: Still gathering info
    # If we don't have a plan yet, ask the LLM to politely ask for the missing info
    if not profile['goal']:
        return llm_bot.chat(user_text, system_instruction="User just spoke. They haven't set a fitness goal yet. Ask them what their goal is.")
    
    if not profile['equipment']:
        return llm_bot.chat(user_text, system_instruction=f"User wants to do {profile['goal']}. Ask them what equipment they have available.")

    return llm_bot.chat(user_text)

# --- UI RENDERING ---
st.title("FitBot Pro ⚡")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(message["content"], unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = determine_response(prompt)
            st.markdown(response, unsafe_allow_html=True)
            
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧠 Brain Info")
    st.write("Model: **Llama 3 (via Groq)**")
    st.write("Strategy: **RAG (Rule + LLM)**")
    st.divider()
    st.write("Context:")
    st.json(st.session_state.user_profile)
    if st.button("Reset Chat"):
        st.session_state.user_profile = {"goal": None, "equipment": None, "injury": "", "experience": "beginner"}
        st.session_state.messages = []
        st.rerun()