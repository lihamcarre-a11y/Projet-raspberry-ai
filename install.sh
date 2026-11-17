#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Raspberry AI — installation ==="

if ! command -v ollama >/dev/null 2>&1; then
  echo "[1/5] Installation d'Ollama…"
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "[1/5] Ollama déjà installé"
fi

echo "[2/5] Démarrage d'Ollama et téléchargement du modèle…"
sudo systemctl enable --now ollama 2>/dev/null || true
sleep 2
ollama pull "${OLLAMA_MODEL:-qwen2.5:1.5b-instruct-q4_K_M}"

echo "[3/5] Installation de Piper…"
PIPER_DATA="${PIPER_DATA:-$HOME/.local/share/piper}"
mkdir -p "$PIPER_DATA"
if ! command -v "${PIPER_BIN:-piper}" >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/piper" ]; then
  ARCH=$(uname -m)
  case "$ARCH" in
    aarch64) PIPER_ASSET="piper_linux_aarch64.tar.gz" ;;
    armv7l)  PIPER_ASSET="piper_linux_armhf.tar.gz" ;;
    x86_64)  PIPER_ASSET="piper_linux_amd64.tar.gz" ;;
    *) echo "Architecture non supportée : $ARCH"; exit 1 ;;
  esac
  curl -fsSL "https://github.com/rhasspy/piper/releases/latest/download/$PIPER_ASSET" -o /tmp/piper.tar.gz
  tar -xzf /tmp/piper.tar.gz -C /tmp
  mkdir -p "$HOME/.local/bin"
  cp /tmp/piper/piper "$HOME/.local/bin/piper"
  chmod +x "$HOME/.local/bin/piper"
fi
export PIPER_BIN="${PIPER_BIN:-$HOME/.local/bin/piper}"

echo "[4/5] Téléchargement de la voix française…"
VOICE="${PIPER_VOICE:-fr_FR-siwis-medium}"
if [ ! -f "$PIPER_DATA/$VOICE.onnx" ]; then
  BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/$VOICE/medium"
  curl -fsSL "$BASE/$VOICE.onnx" -o "$PIPER_DATA/$VOICE.onnx"
  curl -fsSL "$BASE/$VOICE.onnx.json" -o "$PIPER_DATA/$VOICE.onnx.json"
fi

echo "[5/5] Installation des dépendances Python…"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo
echo "Installation terminée. Lancez ./start.sh"
