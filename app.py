import gradio as gr
from config import APP_PASSWORD, MODEL_NAME
from core import load_system_prompt, load_papers, respond
import os

# ===== Load prompt & papers =====
system_prompt = load_system_prompt()
papers = load_papers()

# ===== Session usage counters =====
session_tokens = 0
session_messages = 0

# ===== Admin secret from HF environment =====
admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # fallback default

# ===== Chat handler =====
def chat_handler(message, history, tts_enabled):
    global session_tokens, session_messages
    reply, audio_path, _, cost, tokens_used = respond(
        message, history, tts_enabled, papers, system_prompt
    )
    session_tokens += tokens_used
    session_messages += 1
    return reply, audio_path

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
with gr.Blocks() as app:
    # Login block
    with gr.Row(visible=True) as login_row:
        password = gr.Textbox(label="Clave", type="password", scale=4)
        login_btn = gr.Button("Entrar", scale=1, min_width=80)

    # Main chat interface block (full width)
    chat_row = gr.Column(visible=False)
    with chat_row:
        gr.HTML("""
            <h1>🧠 Mia - IA para Psicología</h1>
            <p>¡Te ayuda a estudiar y a guiarte hacia el conocimiento sobre la investigación! 😉</p>
        """)

        chatbot = gr.ChatInterface(
            fn=chat_handler,
            title="¿Cómo te puedo ayudar hoy?",
            chatbot=gr.Chatbot(type="messages"),
            #additional_inputs=[tts_toggle],
            additional_outputs=[gr.Audio(type="filepath", autoplay=True)],
            type="messages"
        )

        #tts_toggle = gr.Checkbox(label="🔊 Activar respuesta por voz", value=False)
        
    login_btn.click(fn=check_password, inputs=password, outputs=[login_row, chat_row])

    # Admin Panel
    with gr.Accordion("🔧 Admin Panel", open=False):
        admin_pw = gr.Textbox(label="Clave de admin", type="password")
        admin_view = gr.Textbox(label="Uso de sesión", interactive=False)
        check_admin = gr.Button("Ver estado")

        check_admin.click(fn=show_admin_info, inputs=admin_pw, outputs=admin_view)

app.launch()
