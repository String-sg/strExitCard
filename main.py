import pathlib
import shutil
from bs4 import BeautifulSoup
import streamlit as st
from groq import Groq
from st_copy_to_clipboard import st_copy_to_clipboard
import urllib.parse
import os
import uuid
import html

# Streamlit page configuration
st.set_page_config(
    page_title="Situate Learning",
    page_icon="🌟",
    layout="centered"
)


# Function to inject Google Analytics into index.html
def inject_ga():
    GA_MEASUREMENT_ID = st.secrets["google_analytics"]["measurement_id"]

    GA_SCRIPT = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script id='google_analytics'>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """

    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")

    if not soup.find(id="google_analytics"):
        # Backup the original index.html
        bck_index = index_path.with_suffix('.bck')
        if not bck_index.exists():
            shutil.copy(index_path, bck_index)
        
        # Inject the GA script into the <head> section
        html = str(soup)
        new_html = html.replace('<head>', f'<head>\n{GA_SCRIPT}')
        index_path.write_text(new_html)

# Inject Google Analytics
inject_ga()

# Initialize the Groq client
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
client = Groq()

if "session_uuid" not in st.session_state:
    st.session_state.update({
        "session_uuid": str(uuid.uuid4()),
        "teacher_input": "",
        "ai_response": "",
        "ga_initialized": False
    })


def log_event_to_ga(input_text):
    # Sanitize the input to prevent breaking JavaScript
    sanitized_input = html.escape(input_text).replace("\n", "\\n").replace("\r", "\\r")
    
    # Inject custom Google Analytics event script
    event_script = f"""
    <script>
        gtag('event', 'user_input', {{
            'event_category': 'User Interaction',
            'event_label': 'Teacher Input',
            'value': '{sanitized_input}'
        }});
    </script>
    """
    st.markdown(event_script, unsafe_allow_html=True)


# Function to display the help modal
# @st.dialog("Get Started", width="small")
# def help_modal():
#     st.write("Not braining today? Type in a simple concept to trigger a list of questions to better frame or close the lesson.")
#     st.markdown("For example:")
#     st.markdown("- *photosynthesis*")
#     st.markdown("- *algebra basics*")
#     st.markdown("- *moments (physics)*")
#     st.markdown("- *acids, salts and bases (chemistry)*")
#     st.markdown("- *price elasticity of demand*")
#     if st.button("Close Help"):
#         st.rerun()  # Close the modal by triggering a script rerun

# Streamlit Page Title
st.title("🌟 Situate Learning")

# # Help/Get Started Button
# if st.button("Help / Get Started"):
#     help_modal()  # Open the help modal

# Teacher input field
st.markdown("### What did you teach today?")
st.session_state.teacher_input = st.text_input(
    "Enter today's lesson or topic:",
    value=st.session_state.teacher_input,
    placeholder="e.g. photosynthesis or quadratic equations"
)

# Function to generate higher-order thinking questions based on the lesson
def generate_questions(lesson_text):
    """Generate higher-order thinking questions using Groq and Llama."""
    try:
        messages = [
            {"role": "system", "content": "You are an enthusiastic, curious teacher assistant creating thought-provoking questions."},
            {"role": "user", "content": f"Teacher: {lesson_text} Can you create some engaging, higher-order thinking questions related to this topic? Include interdisciplinary questions."}
        ]
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        ai_response = response.choices[0].message.content.strip()
        return ai_response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "Sorry, we couldn't generate questions. Please try again later."


# Button to generate questions
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

# Function to copy response to clipboard
def copy_to_clipboard_script(response):
    sanitized_response = html.escape(response).replace("\n", "\\n").replace("\r", "\\r")
    return f"""
    <script>
    function copyToClipboard() {{
        navigator.clipboard.writeText("{sanitized_response}")
        .then(() => {{
            alert('Copied to clipboard!');
        }})
        .catch(err => {{
            console.error('Failed to copy: ', err);
        }});
    }}
    </script>
    """


# Footer and Feedback Section

# Check if AI response exists
if st.session_state.ai_response:
    # Add the Copy to Clipboard button
    st_copy_to_clipboard(
        st.session_state.ai_response,  # Text to copy
    )
    st.markdown("---")


    # Feedback Link
    st.markdown(
        """
        <div style='text-align: center;'>
            <a href="https://leekahhow.notion.site/14ac34bc89df803fbb5fc9b2922a62ea?pvs=105" target="_blank">
                Provide Feedback
            </a>
        </div>
        """, unsafe_allow_html=True
    )

# Footer with Session ID
st.markdown(
    f"<div style='text-align: center; color: grey;'>Session ID: {st.session_state.session_uuid}</div>",
    unsafe_allow_html=True
)
