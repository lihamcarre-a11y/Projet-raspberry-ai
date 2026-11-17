import json
from collections import deque

import httpx

from .config import HISTORY_LIMIT, OLLAMA_MODEL, OLLAMA_URL, SYSTEM_PROMPT

_history = deque(maxlen=HISTORY_LIMIT)


def get_history():
    return list(_history)


def add_message(role, content):
    _history.append({"role": role, "content": content})


async def chat(messages):
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]


async def chat_stream(messages):
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token


def build_messages():
    return [{"role": "system", "content": SYSTEM_PROMPT}] + get_history()
