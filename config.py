import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_default_key")
APP_PASSWORD = os.getenv("APP_PASSWORD", "default_password")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
SYSTEM_PROMPT_PATH = "prompt.txt"
