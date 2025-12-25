# FitBot: AI-Powered Personal Trainer

FitBot is a Natural Language Processing (NLP) chatbot designed to generate personalized workout recommendations. It combines **Rule-Based Reasoning** (for safety and effectiveness) with **Large Language Models (Llama 3)** for a natural, engaging conversational experience.

## Features
*   **Smart Intent Recognition:** Understands if you want to work out, modify a plan, or just chat.
*   **Entity Extraction:** Automatically detects your Goal (e.g., "Muscle Gain"), Equipment (e.g., "Dumbbells"), and Constraints (e.g., "Knee Pain").
*   **Safety First Logic:** Rules engine prevents recommending dangerous exercises if you have an injury.
*   **RAG Architecture:** Uses **Llama 3 (via Groq)** to provide expert commentary and explain *why* a workout was chosen.
*   **Modern UI:** Sleek Dark Mode interface built with Streamlit.

## Tech Stack
*   **Language:** Python 3.9+
*   **NLP:** Scikit-Learn (SVM Classifier), SpaCy concepts
*   **LLM:** Llama 3.3 (via Groq API)
*   **Interface:** Streamlit
*   **Database:** JSON (Knowledge Base)

## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/shahmir2004/FitBot.git
    cd FitBot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment Variables**
    *   Create a `.env` file in the root directory.
    *   Add your Groq API Key:
        ```text
        GROQ_API_KEY=gsk_your_key_here
        ```

4.  **Run the App**
    ```bash
    streamlit run src/app.py
    ```
