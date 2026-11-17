import io
import threading
import wave

import numpy as np

from .config import WHISPER_MODEL

_model = None
_lock = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _model


def wav_to_float32(wav_bytes: bytes) -> np.ndarray:
    with wave.open(io.BytesIO(wav_bytes)) as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())
    if sample_width == 2:
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    elif sample_width == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"Largeur d'échantillon non supportée : {sample_width}")
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    return audio


def transcribe(wav_bytes: bytes, language: str = "fr") -> str:
    model = get_model()
    audio = wav_to_float32(wav_bytes)
    segments, _ = model.transcribe(audio, language=language, beam_size=1)
    return " ".join(segment.text.strip() for segment in segments).strip()
