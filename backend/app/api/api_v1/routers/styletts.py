import os
import io
import uuid
import torch
import numpy as np
import torchaudio
import logging
from pydub import AudioSegment
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
from faster_whisper import WhisperModel
from app.data_models.schemas import UserQuery
from app.styleTTS2.run_tts import LFinference


import os
from pydub import AudioSegment

# 🔧 Set explicit paths for FFmpeg + FFprobe
ffmpeg_path = r"C:\ffmpeg\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\ffmpeg\ffmpeg-8.0-essentials_build\bin\ffprobe.exe"

AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Also ensure PATH includes them
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)




# --- Setup ---
logger = logging.getLogger(__name__)
audio_router = r = APIRouter()
device = "cuda" if torch.cuda.is_available() else "cpu"

# ==============================================================
# 🔹 Initialize FasterWhisper
# ==============================================================
logger.info("Loading FasterWhisper model (medium.en)...")
whisper_model = WhisperModel("medium.en", device=device, compute_type="float16" if device == "cuda" else "int8")
logger.info("✅ FasterWhisper model loaded successfully.")

# Custom temp directory for safe file I/O
TEMP_DIR = os.path.join(os.getcwd(), "temp_files")
os.makedirs(TEMP_DIR, exist_ok=True)


# ==============================================================
# 🔹 1. WebSocket: Receive audio chunks and transcribe locally
# ==============================================================
@r.websocket("/listen")
async def get_audio_chunk(websocket: WebSocket):
    """Receive audio chunks, transcribe with FasterWhisper, send text back."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            transcript = transcribe_with_faster_whisper(data)
            await websocket.send_text(transcript)
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected by client.")
    except Exception as e:
        logger.error(f"❌ Error in WebSocket processing: {e}")
        try:
            await websocket.send_text(f"Error: {e}")
        except Exception:
            pass
    finally:
        if not websocket.client_state.name.lower().startswith("close"):
            try:
                await websocket.close()
            except Exception:
                pass


# ==============================================================
# 🔹 2. Transcription (Local FasterWhisper)
# ==============================================================
def transcribe_with_faster_whisper(audio_chunk: bytes) -> str:
    """Transcribe audio chunk using local FasterWhisper."""
    temp_path = None
    try:
        temp_path = os.path.join(TEMP_DIR, f"chunk_{uuid.uuid4().hex}.wav")
        with open(temp_path, "wb") as f:
            f.write(audio_chunk)

        # Convert MP3/unknown format to WAV for whisper input
        wav_path = temp_path.replace(".wav", "_converted.wav")
        AudioSegment.from_file(temp_path).export(wav_path, format="wav")

        segments, _ = whisper_model.transcribe(wav_path, beam_size=5)
        transcript = " ".join(segment.text.strip() for segment in segments)

        logger.info(f"🧠 Transcript: {transcript}")
        return transcript or "No speech detected"

    except Exception as e:
        logger.error(f"❌ FasterWhisper transcription failed: {e}")
        return "Transcription error"

    finally:
        for f in [temp_path, temp_path.replace(".wav", "_converted.wav")]:
            try:
                if f and os.path.exists(f):
                    os.chmod(f, 0o666)
                    os.remove(f)
                    logger.debug(f"🧹 Deleted temp file: {f}")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup failed: {cleanup_error}")


# ==============================================================
# 🔹 3. TTS Endpoint (unchanged)
# ==============================================================
@r.post("/tts")
async def generate_tts(user_query: UserQuery):
    """Generate speech audio using StyleTTS2."""
    text = user_query.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty")

    logger.info(f"TTS request received: {text}")
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    wavs, s_prev = [], None

    for sentence in sentences:
        noise = torch.randn(1, 1, 256).to(device)
        wav, s_prev = LFinference(
            sentence + ".", s_prev, noise,
            alpha=0.7, diffusion_steps=20, embedding_scale=1
        )
        wavs.append(wav)

    wav = np.concatenate(wavs)
    temp_audio_path = os.path.join(TEMP_DIR, f"tts_{uuid.uuid4().hex}.wav")
    torch_wav = torch.from_numpy(wav).reshape(1, -1)
    torchaudio.save(temp_audio_path, torch_wav, 24000)

    def stream_audio():
        with open(temp_audio_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
        try:
            os.remove(temp_audio_path)
            logger.info(f"🧹 Deleted TTS file: {temp_audio_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete TTS file: {e}")

    return StreamingResponse(stream_audio(), media_type="audio/wav")
