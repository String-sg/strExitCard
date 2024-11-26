import streamlit as st
from groq import Groq
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

if "ga_initialized" not in st.session_state:
    st.session_state.ga_initialized = True
    GA_MEASUREMENT_ID = st.secrets["google_analytics"]["measurement_id"]

    GA_SCRIPT = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """
    st.markdown(GA_SCRIPT, unsafe_allow_html=True)



def log_event_to_ga(input_text):
    sanitized_input = html.escape(input_text)  # Escape special characters
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
    sanitized_response = html.escape(response)
    return f"""
    <script>
    function copyToClipboard() {{
        navigator.clipboard.writeText("{sanitized_response}");
        alert('Copied to clipboard!');
    }}
    </script>
    """


# Share and Feedback Section
st.markdown("---")

# Telegram and WhatsApp Links
def encode_response(response):
    return urllib.parse.quote(response.strip())

if st.session_state.ai_response:
    response_encoded = encode_response(st.session_state.ai_response)
    telegram_link = f"https://t.me/share/url?url={response_encoded}"
    whatsapp_link = f"https://api.whatsapp.com/send?text={response_encoded}"


# Footer with Share Buttons and Feedback Link
if st.session_state.ai_response:
    # Encode the response for URL
    response_encoded = st.session_state.ai_response.replace(" ", "%20")

    # Telegram and WhatsApp Links
    telegram_link = f"https://t.me/share/url?url={response_encoded}"
    whatsapp_link = f"https://api.whatsapp.com/send?text={response_encoded}"

    # Display buttons
    st.markdown(f"""
        <div style='text-align: center;'>
            <a href="{telegram_link}" target="_blank">
                <button>Send to Telegram</button>
            </a>
            <a href="{whatsapp_link}" target="_blank">
                <button>Send to WhatsApp</button>
            </a>
            <button onclick="copyToClipboard()">Copy to Clipboard</button>
        </div>
    """, unsafe_allow_html=True)

    # Add JavaScript to handle copy-to-clipboard functionality
    st.markdown(copy_to_clipboard_script(st.session_state.ai_response), unsafe_allow_html=True)

# Feedback Link
st.markdown(
    """
    <div style='text-align: center;'>
        <a href="https://leekahhow.notion.site/14ac34bc89df803fbb5fc9b2922a62ea?pvs=105" target="_blank">
            Provide Feedback
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


# Footer with Session ID
st.markdown(
    f"<div style='text-align: center; color: grey; font-size: small;'>Session ID: {st.session_state.session_uuid}</div>",
    unsafe_allow_html=True
)
