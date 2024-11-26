import streamlit as st
from groq import Groq
import os
import uuid
from add_ga import inject_ga

# Streamlit page configuration
st.set_page_config(
    page_title="Situate Learning",
    page_icon="🌟",
    layout="centered"
)

# Initialize the Groq client
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
client = Groq()

# Initialize Streamlit session states
if "session_uuid" not in st.session_state:
    st.session_state.session_uuid = str(uuid.uuid4())
if "teacher_input" not in st.session_state:
    st.session_state.teacher_input = ""
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

# Streamlit Page Title
st.title("🌟 Situate Learning")
st.markdown(f"**Session ID:** `{st.session_state.session_uuid}`")

# Teacher input field
st.markdown("### What did you teach today?")
st.session_state.teacher_input = st.text_area(
    "Enter today's lesson or topic:",
    value=st.session_state.teacher_input,
    placeholder="e.g., We learned calculus and first order derivatives today",
    height=150
)

# Function to generate higher-order thinking questions based on the lesson
def generate_questions(lesson_text):
    """Generate higher-order thinking questions using Groq and Llama."""
    messages = [
        {"role": "system", "content": "You are an enthusiastic, curious teacher assistant creating thought-provoking questions."},
        {"role": "user", "content": f"Teacher: {lesson_text} Can you create some engaging, higher-order thinking questions related to this topic? Make sure to include some that are localized to Southeast Asia and relevant to teenagers."}
    ]
    
    # Using Groq API with Llama to generate questions
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    
    # Extract the response from Llama
    ai_response = response.choices[0].message.content.strip()
    return ai_response

# Function to log events to GA
def log_event_to_ga(input_text):
    event_script = f"""
    <script>
        gtag('event', 'user_input', {{
            'event_category': 'User Interaction',
            'event_label': 'Teacher Input',
            'value': '{input_text}'
        }});
    </script>
    """
    st.markdown(event_script, unsafe_allow_html=True)

# Modify the button logic to include event tracking
if st.button("Generate Questions"):
    if st.session_state.teacher_input.strip():
        # Log the user input to GA
        log_event_to_ga(st.session_state.teacher_input)

        # Generate higher-order thinking questions based on teacher's input
        st.session_state.ai_response = generate_questions(st.session_state.teacher_input)
        st.markdown(f"### Higher-Order Thinking Questions:")
        st.write(st.session_state.ai_response)
    else:
        st.warning("Please provide a topic or lesson before submitting.")
