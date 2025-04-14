import gradio as gr
from config import APP_PASSWORD, MODEL_NAME, OPENAI_API_KEY
from core import load_system_prompt, load_papers
import os
import openai

# ===== Load prompt & papers =====
system_prompt = load_system_prompt()
#papers = load_papers()

# ===== Session usage counters =====
session_tokens = 0
session_messages = 0

# ===== Config secrets =====
admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  
openai.api_key = os.getenv("OPENAI_API_KEY", "your_default_key")
model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

# ===== Chat handler =====
def chat_handler(message, history):
    """Called by Gradio when the user submits a message."""
    
    # 1st create the input for the chat, by merging history with request
    chat_input = history.append({"role": "user", "content": message})  # Append the user's message to the history

    # Get response from OpenAI API - we'll be using the newer Responses API
    try:
        response = openai.responses.create(
            model = model_name, 
            instructions = system_prompt,
            input = chat_input,
            temperature=0.6  
        )
        reply = response.output[0].content[0].text
        chat_history.append({"role": "assistant", "content": reply})  # Append the assistant's reply to the history
    except Exception as e:
        reply = f"Error occurred: {str(e)}"

    print(chat_history)
    return chat_history 

# ===== Login gate =====
def check_password(pw):
    if pw == APP_PASSWORD:
        return gr.update(visible=False), gr.update(visible=True)
    return gr.update(error="Clave incorrecta"), gr.update(visible=False)

# ===== UI layout =====
css_centered = ".centered-box { margin: auto; width: 300px; text-align: center; }"

with gr.Blocks() as app:
    # Login block
    with gr.Group(visible=True, elem_classes= css_centered) as login_block:
        with gr.Row():
            gr.Markdown(
                """
                <h1>🔑 Acceso a Mia</h1>
                <p>Por favor, introduce la clave.</p>
                """
            )

        with gr.Row():
            password = gr.Textbox(label="Clave", type="password")

        with gr.Row():
            login_btn = gr.Button("Entrar")

    # Main chat interface block (full width)
    with gr.Group(visible=False) as chat_block:
        with gr.Row():
            gr.HTML("""
                <h1>🧠 Mia - IA para Psicología</h1>
                <p>¡Te ayuda a estudiar y a guiarte hacia el conocimiento sobre la investigación! 😉</p>
            """)

        with gr.Row():
            chat_history = gr.ChatInterface(fn=chat_handler, type="messages")

    login_btn.click(
        fn=check_password, 
        inputs=password, 
        outputs=[login_block, chat_block])

app.launch()
