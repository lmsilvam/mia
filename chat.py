import streamlit as st
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from utils import search_papers

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_response(client, model_name, messages_for_api):
    """Gets a response from OpenAI based on chat history."""
    response = client.chat.completions.create(
        model=model_name,
        messages=messages_for_api,
        max_tokens=250,
        temperature=0.6,
        stop=None
    )
    return response.choices[0].message.content

def display_chat_history():
    """Displays chat history stored in session state."""
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def append_to_history(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    with st.chat_message(role):
        st.markdown(content)

def handle_user_input(papers):
    """Handles user input and generates assistant response."""
    if prompt := st.chat_input("¿Cómo te puedo ayudar hoy?"):
        append_to_history("user", prompt)

        # Contextual paper excerpts
        relevant_excerpts = search_papers(prompt, papers) if papers else []
        messages_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        if relevant_excerpts:
            messages_for_api.append({
                "role": "system",
                "content": "Contenido relevante:\n" + "\n".join(relevant_excerpts)
            })

        # Get response and display it
        assistant_response = get_openai_response(client, MODEL_NAME, messages_for_api)
        append_to_history("assistant", assistant_response)

def chat_interface(papers):
    """Displays the chat UI and integrates search functionality."""
    st.title("Mia - AI para Investigación en Psicología")
    st.write("Soy tu IA para la clase. Puedo darte respuestas generales pero no puedo hacer cálculos por ti. Pregúntame algo.")

    display_chat_history()
    handle_user_input(papers)
