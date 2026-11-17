const chat = document.getElementById("chat");
const textInput = document.getElementById("text-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const clearBtn = document.getElementById("clear-btn");
const statusEl = document.getElementById("status");

function setStatus(text) {
  statusEl.textContent = text || "";
}

function addMessage(role, text, pending = false) {
  const div = document.createElement("div");
  div.className = `msg ${role}${pending ? " pending" : ""}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

async function sendText() {
  const message = textInput.value.trim();
  if (!message) return;
  textInput.value = "";
  addMessage("user", message);
  const pending = addMessage("assistant", "…", true);
  setStatus("Réflexion en cours…");
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) throw new Error((await response.json()).detail || response.statusText);
    const data = await response.json();
    pending.textContent = data.reply;
    speak(data.reply);
  } catch (err) {
    pending.textContent = `Erreur : ${err.message}`;
  } finally {
    setStatus("");
  }
}

function speak(text) {
  if (!("speechSynthesis" in window) || !text) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "fr-FR";
  window.speechSynthesis.speak(utterance);
}

let mediaStream = null;
let audioContext = null;
let recorder = null;

function encodeWav(samples, sampleRate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  const writeString = (offset, str) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  };
  writeString(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, samples.length * 2, true);
  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Blob([view], { type: "audio/wav" });
}

async function startRecording() {
  mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  audioContext = new AudioContext({ sampleRate: 16000 });
  const source = audioContext.createMediaStreamSource(mediaStream);
  const processor = audioContext.createScriptProcessor(4096, 1, 1);
  const chunks = [];
  processor.onaudioprocess = (event) => {
    chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));
  };
  source.connect(processor);
  processor.connect(audioContext.destination);
  recorder = { processor, source, chunks };
}

async function stopRecording() {
  if (!recorder) return;
  const { processor, source, chunks } = recorder;
  processor.disconnect();
  source.disconnect();
  mediaStream.getTracks().forEach((track) => track.stop());
  await audioContext.close();
  recorder = null;

  const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
  if (totalLength < 16000) {
    setStatus("Enregistrement trop court");
    return;
  }
  const samples = new Float32Array(totalLength);
  let offset = 0;
  for (const chunk of chunks) {
    samples.set(chunk, offset);
    offset += chunk.length;
  }
  const wavBlob = encodeWav(samples, audioContext.sampleRate || 16000);

  addMessage("user", "🎤 …");
  const pending = addMessage("assistant", "…", true);
  setStatus("Transcription et réflexion…");
  try {
    const form = new FormData();
    form.append("file", wavBlob, "recording.wav");
    const response = await fetch("/api/voice", { method: "POST", body: form });
    if (!response.ok) throw new Error((await response.json()).detail || response.statusText);
    const data = await response.json();
    chat.lastElementChild.previousElementSibling.textContent = data.query || "🎤 (vide)";
    pending.textContent = data.reply || "(aucune réponse)";
    if (data.audio) {
      const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
      audio.play();
    } else {
      speak(data.reply);
    }
  } catch (err) {
    pending.textContent = `Erreur : ${err.message}`;
  } finally {
    setStatus("");
  }
}

micBtn.addEventListener("click", async () => {
  if (recorder) {
    micBtn.classList.remove("recording");
    await stopRecording();
  } else {
    try {
      await startRecording();
      micBtn.classList.add("recording");
      setStatus("Enregistrement… cliquez pour arrêter");
    } catch (err) {
      setStatus("Micro inaccessible : " + err.message);
    }
  }
});

sendBtn.addEventListener("click", sendText);
textInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendText();
});

clearBtn.addEventListener("click", async () => {
  chat.innerHTML = "";
  await fetch("/api/history", { method: "DELETE" }).catch(() => {});
});

(async () => {
  try {
    const response = await fetch("/api/history");
    const data = await response.json();
    for (const message of data.messages) {
      if (message.role === "user" || message.role === "assistant") {
        addMessage(message.role, message.content);
      }
    }
  } catch (err) {
    setStatus("Impossible de charger l'historique");
  }
})();
