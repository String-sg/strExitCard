
"""
Situate Learning - A Streamlit app that generates higher-order thinking questions
using Groq's LLM API based on teacher input.
"""
import os
import uuid
import html
import streamlit as st
from groq import Groq
from st_copy_to_clipboard import st_copy_to_clipboard

# Streamlit page configuration
st.set_page_config(
    page_title="Situate Learning",
    page_icon="🌟",
    layout="centered"
)

# Initialize the Groq client
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    client = Groq()
except Exception as e:
    st.error("Please set up GROQ_API_KEY in Replit Secrets")
    st.stop()

def initialize_session_state():
    """Initialize the session state variables."""
    if "session_uuid" not in st.session_state:
        st.session_state.update({
            "session_uuid": str(uuid.uuid4()),
            "teacher_input": "",
            "ai_response": ""
        })

def generate_questions(lesson_text):
    """
    Generate higher-order thinking questions using Groq and Llama.
    
    Args:
        lesson_text (str): The lesson or topic input by the teacher
        
    Returns:
        str: Generated questions from the LLM
    """
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an enthusiastic, curious teacher assistant creating thought-provoking questions."
            },
            {
                "role": "user",
                "content": f"Teacher: {lesson_text} Can you create some engaging, "
                          "higher-order thinking questions related to this topic? Include interdisciplinary questions."
            }
        ]
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Sorry, we couldn't generate questions. Please try again later."

def copy_to_clipboard_script(response):
    """Generate JavaScript code for copying text to clipboard."""
    sanitized_response = html.escape(response).replace("\n", "\\n").replace("\r", "\\r")
    return f"""
    <script>
    function copyToClipboard() {{
        navigator.clipboard.writeText("{sanitized_response}")
        .then(() => {{ alert('Copied to clipboard!'); }})
        .catch(err => {{ console.error('Failed to copy: ', err); }});
    }}
    </script>
    """

def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()
    
    st.title("🌟 Situate Learning")
    
    st.markdown("### What did you teach today?")
    st.session_state.teacher_input = st.text_input(
        "Enter today's lesson or topic:",
        value=st.session_state.teacher_input,
        placeholder="e.g. photosynthesis or quadratic equations"
    )

    if st.button("Generate Questions"):
        if st.session_state.teacher_input.strip():
            st.session_state.ai_response = generate_questions(st.session_state.teacher_input)
            st.markdown("### Higher-Order Thinking Questions:")
            st.write(st.session_state.ai_response)
        else:
            st.warning("Please provide a topic or lesson before submitting.")

    if st.session_state.ai_response:
        st_copy_to_clipboard(st.session_state.ai_response)
        st.markdown("---")
        
        st.markdown(
            """
            <div style='text-align: center;'>
                <a href="https://leekahhow.notion.site/14ac34bc89df803fbb5fc9b2922a62ea?pvs=105" 
                target="_blank">Provide Feedback</a>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"<div style='text-align: center; color: grey;'>Session ID: {st.session_state.session_uuid}</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
