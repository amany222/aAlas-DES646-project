# RecoDR: Bilingual AI Voice-to-Text Learning Aid

**GitHub Repository:** `https://github.com/amany222/aAlas-DES646-project`

A real-time, bilingual (English/Hindi), on-device AI system that transcribes live speech to text and synthesizes text to expressive speech. This system is designed as an accessibility tool for hearing-impaired students in a classroom environment.

## 1\. Problem Statement

For students with hearing impairments, the fast-paced, verbal environment of a traditional classroom presents a major accessibility barrier. Live lectures, discussions, and presentations are inaccessible. Traditional solutions like human interpreters or post-processed captions often lack immediacy, are costly, or are simply unavailable. This project directly addresses the need for an immediate, reliable, and on-demand communication bridge.

## 2\. Our Solution: RecoDR

**aAlas** is a real-time, local-first AI pipeline that runs entirely on a standard laptop (no internet required). It provides a two-way communication bridge:

1.  **Voice-to-Text (VTT):** It captures the teacher's speech via a microphone, transcribes it in real-time using `FasterWhisper`, and displays the text on the student's screen.
    
2.  **Text-to-Voice (TTV):** It allows the student to type a question or response, which is then synthesized into a natural-sounding, expressive voice using `StyleTTS2` to be played for the class.
    

## 3\. Key Features

*   **Real-Time Transcription:** Uses `FasterWhisper` for low-latency, on-device speech-to-text.
    
*   **Expressive Speech Synthesis:** Employs `StyleTTS2` to generate high-quality, natural-sounding speech, avoiding a robotic-sounding voice.
    
*   **Offline-First:** No cloud APIs are used. The entire pipeline runs locally, ensuring 100% user privacy and zero operational costs.
    
*   **CPU Optimized:** Quantized models (`int8`) and an asynchronous backend allow the full pipeline to run efficiently on a standard laptop CPU.
    
*   **Bilingual:** Fully supports both English and Hindi for transcription and synthesis.
    
*   **Low Latency:** Achieves a usable end-to-end latency of ~3.7 seconds, which is suitable for a classroom setting.
    

## 4\. Technology Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| Frontend | React | Modern, component-based UI for dynamic text display and audio handling. |
| Backend | Flask + FastAPI (hybrid) | Serves the models and handles real-time data flow. |
| Server | Uvicorn | High-performance ASGI server for FastAPI and WebSocket connections. |
| Communication | WebSockets | Full-duplex, low-latency communication between frontend and backend. |
| ASR Model | FasterWhisper | CTranslate2-optimized Whisper model for fast CPU transcription. |
| TTS Model | StyleTTS2 | For high-fidelity, expressive, and controllable speech synthesis. |
| Phonemizer | eSpeak NG | A required pre-processor for StyleTTS2 to convert text to phonemes. |
| Audio Utils | ffmpeg, pydub | Essential for audio format conversion, slicing, and manipulation. |

## 5\. Getting Started

### Prerequisites

This system has critical **external dependencies** that are **not** Python packages. You must install them on your system first.

1.  **FFmpeg:**
    
    *   **Why:** Used by `pydub` and `FasterWhisper` for audio processing and conversion.
        
    *   **Install:** Download the binaries from [ffmpeg.org](https://ffmpeg.org/download.html "null") or install via a package manager (e.g., `choco install ffmpeg` on Windows, `apt install ffmpeg` on Ubuntu).
        
    *   **Verify:** Ensure `ffmpeg` is added to your system's `PATH`.
        
2.  **eSpeak NG:**
    
    *   **Why:** Required by the `phonemizer` library as the backend for `StyleTTS2`.
        
    *   **Install:** Download and run the official installer from [github.com/espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng/releases "null").
        
    *   **Verify:** The `libespeak-ng.dll` (Windows) or `libespeak-ng.so` (Linux) file must be accessible.
        

### Installation & Setup

1.  **Clone the repository:**
    
        git clone [https://github.com/amany222/aAlas-DES646-project.git](https://github.com/amany222/aAlas-DES646-project.git)
        cd aAlas-DES646-project
        
    
2.  **Set up the Backend (Python):**
    
        cd backend
        
        # Create a virtual environment
        python -m venv venv
        
        # Activate the environment
        # Windows:
        .\venv\Scripts\activate
        # macOS/Linux:
        # source venv/bin/activate
        
        # Install Python dependencies from requirements.txt
        pip install -r requirements.txt
        
        # Download NLTK models (required by StyleTTS2)
        python -m nltk.downloader punkt punkt_tab
        
    
3.  **Set Environment Variables (CRITICAL):** You _must_ tell `phonemizer` where to find the `eSpeak NG` library you installed.
    
    *   **Windows (Command Prompt):**
        
            # This path may vary based on your eSpeak NG installation
            setx PHONEMIZER_ESPEAK_LIBRARY "C:\Program Files\eSpeak NG\libespeak-ng.dll"
            
        
    *   **Windows (PowerShell):**
        
            # This path may vary based on your eSpeak NG installation
            [System.Environment]::SetEnvironmentVariable('PHONEMIZER_ESpeak_LIBRARY', 'C:\Program Files\eSpeak NG\libespeak-ng.dll', [System.EnvironmentVariableTarget]::User)
            
        
    *   **macOS/Linux (`.bashrc` or `.zshrc`):**
        
            # This path may vary
            export PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/libespeak-ng.so
            
        
    
    **Restart your terminal or VS Code** after setting environment variables to ensure they are loaded.
    
4.  **Set up the Frontend (React):**
    
        # Open a new terminal
        cd ../frontend
        
        # Install npm dependencies
        npm install
        
    

## 6\. How to Run

1.  **Start the Backend Server:**
    
    *   In your first terminal (in the `backend` folder with `venv` activated):
        
    *         # This script in the repo starts the Uvicorn server
              python main.py 
              # Or, if you have a run.bat/run.sh
              ./run.bat
            
        
    *   The server will start on `http://127.0.0.1:8000`. Wait until you see the models (FasterWhisper, StyleTTS2) successfully loaded in the console.
        
2.  **Start the Frontend Application:**
    
    *   In your second terminal (in the `frontend` folder):
        
    *         npm start
            
        
    *   This will automatically open your default browser to `http://localhost:3000`.
        
3.  **Use the Application:**
    
    *   The React app will connect to the backend WebSocket.
        
    *   Click "Start Listening" to begin real-time transcription.
        
    *   Type text and click "Speak" to use text-to-speech.
        

## 7\. Performance

All tests were conducted on a **CPU-only** system (Intel Core i7-10750H, 16 GB RAM).

### Latency

| Module | Average Latency (s) | Notes |
| --- | --- | --- |
| Speech-to-Text (FasterWhisper) | 1.2s | "small" model, int8, CPU |
| Text Pre-processing (Phonemizer) | 0.4s | Caching helps subsequent runs |
| Text-to-Speech (StyleTTS2) | 2.1s | 10 diffusion steps, CPU |
| End-to-End Pipeline (Total) | ~3.7s | Smooth real-time operation |

### Accuracy & Quality

*   **ASR (WER):** ~6.5% (English) / ~11.9% (Hindi). This is a minor accuracy trade-off for a significant speedup vs. the standard Whisper model.
    
*   **TTS (MOS):** **4.3 / 5.0**. The speech quality is rated as highly natural and expressive, approaching premium cloud APIs (e.g., Google Wavenet @ 4.6).
    

## 8\. Future Work

*   **Multimodal Output:** Integrate a module to generate visual American Sign Language (ASL) avatars from the transcribed text.
    
*   **Edge Deployment:** Optimize the models (using pruning or quantization) for deployment on low-power edge devices like a Raspberry Pi or NVIDIA Jetson.
    
*   **Emotion-Aware Synthesis:** Fine-tune `StyleTTS2` to recognize and reproduce the emotion or prosody from the _original_ speaker's audio, not just the text.
    

## 9\. License

This project is licensed under the MIT License.
