import os
import subprocess
import tempfile

from .config import PIPER_BIN, PIPER_DATA, PIPER_VOICE


def voice_path() -> str:
    return os.path.join(PIPER_DATA, f"{PIPER_VOICE}.onnx")


def synthesize(text: str) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        out_path = tmp.name
    try:
        subprocess.run(
            [PIPER_BIN, "--model", voice_path(), "--output_file", out_path],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        with open(out_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(out_path)
