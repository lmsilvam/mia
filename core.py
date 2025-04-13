from openai import OpenAI
import os, tempfile, time
from config import OPENAI_API_KEY, MODEL_NAME, SYSTEM_PROMPT_PATH

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
