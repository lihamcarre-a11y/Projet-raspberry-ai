#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama n'est pas installé. Lancez ./install.sh" >&2
  exit 1
fi

if ! curl -fsS "${OLLAMA_URL:-http://127.0.0.1:11434}/api/tags" >/dev/null 2>&1; then
  echo "Démarrage d'Ollama…"
  ollama serve >/dev/null 2>&1 &
  sleep 3
fi

if [ -x ".venv/bin/uvicorn" ]; then
  PYTHON=".venv/bin/python3"
  UVICORN=".venv/bin/uvicorn"
else
  echo "Environnement Python absent. Lancez ./install.sh" >&2
  exit 1
fi

export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b-instruct-q4_K_M}"
export WHISPER_MODEL="${WHISPER_MODEL:-base}"
export PIPER_BIN="${PIPER_BIN:-$HOME/.local/bin/piper}"
export PIPER_VOICE="${PIPER_VOICE:-fr_FR-siwis-medium}"
export PIPER_DATA="${PIPER_DATA:-$HOME/.local/share/piper}"

echo "Raspberry AI démarré sur http://$(hostname -I | awk '{print $1}'):8000"
exec "$UVICORN" server.main:app --host 0.0.0.0 --port 8000 --app-dir .
