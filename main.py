import streamlit as st
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import AdaptionPromptConfig, get_peft_model
from difflib import SequenceMatcher

# Function to calculate similarity score
def calculate_similarity(student_answer, suggested_answer):
    return SequenceMatcher(None, student_answer.lower(), suggested_answer.lower()).ratio()

# Function to use Llama-Adapter for grading
def grade_with_llama(model, tokenizer, question, student_answer, suggested_answer):
    input_prompt = (
        f"Question: {question}\n"
        f"Suggested Answer: {suggested_answer}\n"
        f"Student's Answer: {student_answer}\n"
        f"Grade the student's answer and provide feedback:\n"
    )
    inputs = tokenizer(input_prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=200)
    feedback = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return feedback

# Streamlit app
st.title("Short Answer Grading Assistant with Llama-Adapter")
st.write("Upload a CSV with questions, suggested answers, and guided responses to create a quiz.")

# Load Llama model and tokenizer
@st.cache_resource
def load_llama_adapter():
    model_name = "huggingface/llama-7b"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    base_model = AutoModelForCausalLM.from_pretrained(model_name)
    adapter_config = AdaptionPromptConfig(
        peft_type="Llama-Adapter",
        task_type="CAUSAL_LM",
        adapter_len=10,
        adapter_layers=2
    )
    model = get_peft_model(base_model, adapter_config)
    return model, tokenizer

st.sidebar.header("Llama-Adapter Settings")
if st.sidebar.button("Load Llama-Adapter"):
    with st.spinner("Loading Llama-Adapter..."):
        try:
            llama_model, llama_tokenizer = load_llama_adapter()
            st.success("Llama-Adapter loaded successfully!")
        except Exception as e:
            st.error(f"Error loading Llama-Adapter: {e}")

# CSV upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load CSV
    try:
        data = pd.read_csv(uploaded_file)
        if set(["question", "suggested_answer", "guided_response"]).issubset(data.columns):
            st.success("CSV successfully loaded!")
        else:
            st.error("CSV must contain 'question', 'suggested_answer', and 'guided_response' columns.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()

    # Initialize quiz session
    st.session_state.current_index = st.session_state.get("current_index", 0)
    st.session_state.score = st.session_state.get("score", 0)

    # Display question
    if st.session_state.current_index < len(data):
        question_row = data.iloc[st.session_state.current_index]
        question = question_row["question"]
        suggested_answer = question_row["suggested_answer"]
        guided_response = question_row["guided_response"]

        st.subheader(f"Question {st.session_state.current_index + 1}")
        st.write(question)

        # Student response
        student_answer = st.text_area("Your Answer", key=f"answer_{st.session_state.current_index}")

        if st.button("Submit Answer"):
            with st.spinner("Grading your answer..."):
                try:
                    if "llama_model" in locals():
                        feedback = grade_with_llama(
                            llama_model, llama_tokenizer, question, student_answer, suggested_answer
                        )
                    else:
                        feedback = (
                            f"**Similarity Score:** {calculate_similarity(student_answer, suggested_answer) * 100:.2f}%\n"
                            f"Suggested Answer: {suggested_answer}\n"
                            f"Guided Response: {guided_response}"
                        )
                    st.write("**Feedback:**")
                    st.write(feedback)
                except Exception as e:
                    st.error(f"Error grading answer: {e}")

            # Move to the next question
            st.session_state.current_index += 1
            st.experimental_rerun()
    else:
        # Quiz completed
        st.subheader("Quiz Completed!")
        st.write(f"**Your Total Score:** {st.session_state.score / len(data) * 100:.2f}%")
        st.button("Restart Quiz", on_click=lambda: st.session_state.update({"current_index": 0, "score": 0}))

else:
    st.info("Please upload a CSV to start the quiz.")
