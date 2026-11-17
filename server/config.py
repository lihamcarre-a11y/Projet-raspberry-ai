import os


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b-instruct-q4_K_M")
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
PIPER_BIN = os.environ.get("PIPER_BIN", "piper")
PIPER_VOICE = os.environ.get("PIPER_VOICE", "fr_FR-siwis-medium")
PIPER_DATA = os.environ.get("PIPER_DATA", os.path.expanduser("~/.local/share/piper"))

SYSTEM_PROMPT = (
    "Tu es un assistant personnel qui tourne localement sur un Raspberry Pi. "
    "Réponds en français, de façon concise et utile."
)

HISTORY_LIMIT = 20
