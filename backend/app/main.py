from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.routers.styletts import audio_router
import uvicorn
import tempfile, os
import atexit
import shutil


import os
from dotenv import load_dotenv

# ✅ Force load .env from app directory explicitly
env_path = os.path.join(os.path.dirname(__file__), "app", ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(dotenv_path=env_path)

print(f"✅ Loaded .env from: {env_path}")
print(f"✅ OPENAI_API_KEY starts with: {os.getenv('OPENAI_API_KEY')[:7]}")

# Now import everything else
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.routers.styletts import audio_router

# ✅ Create a dedicated writable temp folder
custom_temp = os.path.join(os.getcwd(), "temp_files")
os.makedirs(custom_temp, exist_ok=True)

# ✅ Make sure Windows users always have permissions
try:
    import ctypes
    ctypes.windll.kernel32.SetFileAttributesW(custom_temp, 0x80)  # FILE_ATTRIBUTE_NORMAL
except Exception:
    pass

# ✅ Redirect all temp file operations to this folder
tempfile.tempdir = custom_temp
os.environ["TMPDIR"] = custom_temp
os.environ["TEMP"] = custom_temp
os.environ["TMP"] = custom_temp

print(f"✅ Using custom temp directory: {custom_temp}")

# ✅ Clean up temp files on shutdown (optional but safe)
def cleanup_temp():
    try:
        shutil.rmtree(custom_temp, ignore_errors=True)
        os.makedirs(custom_temp, exist_ok=True)
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

atexit.register(cleanup_temp)

# --- FASTAPI APP SETUP ---
app = FastAPI(title="Voice over backend API", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(request: Request):
    return {"message": "Server is up and running!"}

app.include_router(audio_router, prefix="/api/v1", tags=["ASR"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
