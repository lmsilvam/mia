from openai import OpenAI
import os, tempfile, time
from config import OPENAI_API_KEY, MODEL_NAME, SYSTEM_PROMPT_PATH

client = OpenAI(api_key=OPENAI_API_KEY)
COOLDOWN_SECONDS = 5
_last_call_time = 0

def load_system_prompt():
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Eres Mia, una IA experta en Psicología."

def load_papers():
    papers = {}
    for filename in os.listdir():
        if filename.startswith("paper") and filename.endswith(".txt"):
            with open(filename, "r", encoding="utf-8") as f:
                papers[filename] = f.read()
    return papers

def search_papers(query, papers):
    results = []
    for title, content in papers.items():
        if query.lower() in content.lower():
            before, after = content.lower().split(query.lower(), 1)
            snippet = before[-300:] + query + after[:300]
            results.append(f"📄 {title}: ...{snippet}...")
    return results

def respond(message, history, tts_enabled, papers, system_prompt):
    global _last_call_time
    now = time.time()
    if now - _last_call_time < COOLDOWN_SECONDS:
        return "⏳ Espera unos segundos antes de enviar otro mensaje.", None, "Cooldown activo", 0.0, 0

    _last_call_time = now

    messages = [{"role": "system", "content": system_prompt}]
    for user, assistant in history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    relevant_excerpts = search_papers(message, papers)
    if relevant_excerpts:
        messages.append({"role": "system", "content": "Contenido relevante:\n" + "\n".join(relevant_excerpts)})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=300,
        temperature=0.6,
    )

    reply = response.choices[0].message.content
    usage = response.usage
    cost_estimate = (usage.total_tokens / 1000) * (0.002 if "gpt-3.5" in MODEL_NAME else 0.02)
    usage_info = f"🧾 Tokens: {usage.total_tokens} (in: {usage.prompt_tokens}, out: {usage.completion_tokens}) | Estimado: ${cost_estimate:.4f}"

    audio_path = None
    if tts_enabled:
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=reply
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            speech_response.stream_to_file(tmp.name)
            audio_path = tmp.name

    return reply, audio_path, usage_info, cost_estimate, usage.total_tokens

