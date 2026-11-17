# Projet Raspberry AI

IA 100 % locale sur Raspberry Pi, avec interface **chat** et **vocale**, accessible depuis n'importe quel appareil du réseau (PC, téléphone) via un navigateur.

## Architecture

| Composant | Rôle | Technologie |
|---|---|---|
| LLM | Génération des réponses | [Ollama](https://ollama.com) (Qwen2.5 1.5B quantifié, ~1 Go en RAM) |
| STT | Voix → texte | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2, int8) |
| TTS | Texte → voix | [Piper](https://github.com/rhasspy/piper) (voix française) |
| Serveur | API + interface web | FastAPI + Uvicorn |
| Interface | Chat + micro | Page web (HTML/JS), aucun compte, aucune donnée sortante |

Tout tourne sur le Raspberry Pi. Aucune connexion Internet n'est nécessaire après l'installation.

## Matériel recommandé

- Raspberry Pi 4 ou 5 (4 Go suffisent avec le modèle 1.5B)
- Carte micro-SD 32 Go+ (A2 conseillée)
- Microphone et haut-parleurs (USB ou carte son)

## Installation

```bash
git clone https://github.com/lihamcarre-a11y/Projet-raspberry-ai.git
cd Projet-raspberry-ai
./install.sh
```

Le script installe Ollama, télécharge le modèle de langage et la voix Piper, installe les dépendances Python.

## Démarrage

```bash
./start.sh
```

Puis ouvrir `http://<ip-du-raspberry>:8000` depuis un navigateur.

- **Chat** : taper le message et valider.
- **Vocal** : maintenir le bouton micro (ou cliquer pour démarrer/arrêter), la réponse est lue à voix haute.

## Configuration

Variables d'environnement (voir `start.sh`) :

| Variable | Défaut | Description |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Adresse du serveur Ollama |
| `OLLAMA_MODEL` | `qwen2.5:1.5b-instruct-q4_K_M` | Modèle de langage (≤ 1.5B paramètres) |
| `WHISPER_MODEL` | `base` | Taille du modèle Whisper (`tiny`, `base`, `small`) |
| `PIPER_BIN` | `piper` | Chemin du binaire piper |
| `PIPER_VOICE` | `fr_FR-siwis-medium` | Voix Piper |
| `PIPER_DATA` | `~/.local/share/piper` | Dossier des modèles Piper |

## Service systemd (démarrage automatique)

```bash
sudo cp systemd/raspberry-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now raspberry-ai
```

## Structure

```
server/        API FastAPI (chat, STT, TTS, pipeline vocal)
web/           Interface web (chat + micro)
install.sh     Installation complète
start.sh       Démarrage du serveur
systemd/       Service systemd
```
