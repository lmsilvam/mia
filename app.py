import gradio as gr
from config import APP_PASSWORD, MODEL_NAME
from core import load_system_prompt, load_papers, respond
import os
import openai

# ===== Load prompt & papers =====
system_prompt = load_system_prompt()
papers = load_papers()

# ===== Session usage counters =====
session_tokens = 0
session_messages = 0

# ===== Admin secret from HF environment =====
admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # fallback default

# ===== OpenAI API key =====
openai.api_key = os.getenv("OPENAI_API_KEY", "your_default_key")  # fallback default

# ===== Chat handler =====
def chat_handler(message, history=[]):
    messages = [{"role": "system", "content": system_prompt}]
    for user, bot in history:
        if user == "User:":
            messages.append({"role": "user", "content": bot})
        elif user == "Bot:":
            messages.append({"role": "assistant", "content": bot})
    messages.append({"role": "user", "content": message})

    # Get response from OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME, 
            messages=messages,
            temperature=0.7  # Adjust for more or less randomness
        )
        reply = response["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"Error occurred: {str(e)}"

# ===== Login gate =====
def check_password(pw):
    if pw == APP_PASSWORD:
        return gr.update(visible=False), gr.update(visible=True)
    return gr.update(error="Clave incorrecta"), gr.update(visible=False)

# ===== Admin usage panel =====
def show_admin_info(pw):
    if pw != admin_password:
        return "❌ Clave incorrecta"
    cost = (session_tokens / 1000) * (0.002 if "gpt-3.5" in MODEL_NAME else 0.02)
    return f"🧾 Mensajes: {session_messages}\n🔢 Tokens: {session_tokens}\n💸 Estimado: ${cost:.4f}"

# ===== UI layout =====
css_centered = ".centered-box { margin: auto; width: 300px; text-align: center; }"

with gr.Blocks() as app:
    # Login block
    with gr.Group(visible=True, css= css_centered) as login_block:
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
            chat_history = gr.Chatbot(label="Chat", elem_id="chatbot").style(height=400)
            usr_input = gr.TextBox(placeholder="Escribe un mensaje...", label="Mensaje")
            submit_button = gr.Button("Enviar")

    # Interactions
    submit_button.click(
        fn=chat_handler,
        inputs=[usr_input, chat_history],
        outputs=[chat_history, chat_history],
    )        

    login_btn.click(
        fn=check_password, 
        inputs=password, 
        outputs=[login_block, chat_block])

    # Admin Panel
    with gr.Accordion("🔧 Admin Panel", open=False):
        admin_pw = gr.Textbox(label="Clave de admin", type="password")
        admin_view = gr.Textbox(label="Uso de sesión", interactive=False)
        check_admin = gr.Button("Ver estado")

        check_admin.click(fn=show_admin_info, inputs=admin_pw, outputs=admin_view)

app.launch()
