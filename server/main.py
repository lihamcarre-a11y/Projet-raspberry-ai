import base64

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import llm, stt, tts

app = FastAPI(title="Raspberry AI")


class ChatRequest(BaseModel):
    message: str


class TtsRequest(BaseModel):
    text: str


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message vide")
    llm.add_message("user", message)
    messages = llm.build_messages()
    try:
        reply = await llm.chat(messages)
    except Exception as exc:
        llm.add_message("assistant", "")
        raise HTTPException(status_code=502, detail=f"LLM indisponible : {exc}") from exc
    llm.add_message("assistant", reply)
    return {"reply": reply}


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message vide")
    llm.add_message("user", message)
    messages = llm.build_messages()

    async def generate():
        full = []
        try:
            async for token in llm.chat_stream(messages):
                full.append(token)
                yield f"data: {base64.b64encode(token.encode('utf-8')).decode('ascii')}\n\n"
        except Exception as exc:
            yield f"data: {base64.b64encode(f'[erreur: {exc}]'.encode()).decode('ascii')}\n\n"
        llm.add_message("assistant", "".join(full))
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    wav_bytes = await file.read()
    try:
        text = stt.transcribe(wav_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Audio illisible : {exc}") from exc
    return {"text": text}


@app.post("/api/tts")
async def tts_endpoint(request: TtsRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texte vide")
    try:
        audio = tts.synthesize(text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"TTS indisponible : {exc}") from exc
    return StreamingResponse(iter([audio]), media_type="audio/wav")


@app.post("/api/voice")
async def voice_endpoint(file: UploadFile = File(...)):
    wav_bytes = await file.read()
    try:
        text = stt.transcribe(wav_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Audio illisible : {exc}") from exc
    if not text:
        return {"query": "", "reply": "", "audio": ""}
    llm.add_message("user", text)
    messages = llm.build_messages()
    try:
        reply = await llm.chat(messages)
    except Exception as exc:
        llm.add_message("assistant", "")
        raise HTTPException(status_code=502, detail=f"LLM indisponible : {exc}") from exc
    llm.add_message("assistant", reply)
    try:
        audio = tts.synthesize(reply)
        audio_b64 = base64.b64encode(audio).decode("ascii")
    except Exception:
        audio_b64 = ""
    return {"query": text, "reply": reply, "audio": audio_b64}


@app.get("/api/history")
async def history():
    return {"messages": llm.get_history()}


app.mount("/", StaticFiles(directory="web", html=True), name="web")
