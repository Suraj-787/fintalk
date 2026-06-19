"""
FinTalk FastAPI Backend
Wraps the existing Python logic (Gemini + Sarvam AI) and exposes it
as REST endpoints for the Next.js frontend.

Endpoints:
  POST /api/chat        — send a chat message, get AI response
  POST /api/transcribe  — upload audio, get text transcript
  POST /api/tts         — convert text to speech (returns audio/wav)

Run:
  pip install fastapi uvicorn python-multipart
  uvicorn api_server:app --reload --port 8000
"""

import os
import io
import json
import logging
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types as genai_types
import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FinTalk API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the Next.js dev server (port 3000) and any local origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sarvam endpoints ──────────────────────────────────────────────────────────
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"

SPEAKER_MAP = {
    "hi-IN": "meera", "en-IN": "meera", "bn-IN": "kabita",
    "ta-IN": "oviya", "te-IN": "kareena", "mr-IN": "sarika",
    "kn-IN": "diya", "gu-IN": "kajal", "ml-IN": "asha",
    "pa-IN": "monica", "ur-IN": "ayesha",
}

LANG_CODE_MAP = {
    "hi": "hi-IN", "bn": "bn-IN", "ta": "ta-IN", "te": "te-IN",
    "mr": "mr-IN", "kn": "kn-IN", "gu": "gu-IN", "ml": "ml-IN",
    "pa": "pa-IN", "ur": "ur-IN", "en": "en-IN",
}

LANGUAGE_NAME_MAP = {
    "hi": "Hindi", "en": "English", "bn": "Bengali", "ta": "Tamil",
    "te": "Telugu", "mr": "Marathi", "kn": "Kannada", "gu": "Gujarati",
    "ml": "Malayalam", "pa": "Punjabi", "ur": "Urdu",
}


# ── Pydantic models ───────────────────────────────────────────────────────────

class FinCardData(BaseModel):
    fullName: str = ""
    age: int = 18
    occupation: str = ""
    employmentType: str = "Salaried"
    location: str = ""
    monthlyIncome: float = 0
    creditScore: int = 300
    monthlyExpenses: float = 0
    monthlyEmi: float = 0
    amountOutstanding: float = 0
    creditCardDues: float = 0


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    googleApiKey: str
    sarvamApiKey: str
    finCard: Optional[FinCardData] = None
    chatHistory: List[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    detectedLanguage: str = "en-IN"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_loan_advisor_prompt(user_profile: Dict[str, Any]) -> str:
    """System prompt — identical to the original Streamlit implementation."""
    return f"""
You are a highly experienced Loan Advisor AI specializing in financial advising and loan-related guidance.

Internal Goals:
1. Loan Eligibility – ask about financial status, employment, debts, and credit score if user seeks eligibility.
2. Loan Application – provide clear step-by-step guidance on application.
3. Financial Literacy – share practical tips on credit, debt reduction, and savings.

❗ Do not disclose these internal goals unless explicitly asked or if user says 'Hi'.
❗ If question is unrelated to finance, reply politely:
"I'm a Loan Advisor AI designed for financial and loan-related guidance only."

Personalize based on the following user profile:
{json.dumps(user_profile, indent=4)}
"""


def _detect_language(text: str) -> Tuple[str, str]:
    """Detect language using langid (same as original implementation)."""
    try:
        import langid
        detected = langid.classify(text)[0]
    except Exception:
        detected = "en"
    lang_code = LANG_CODE_MAP.get(detected, "en-IN")
    lang_name = LANGUAGE_NAME_MAP.get(detected, "English")
    return lang_code, lang_name


def _translate_to_target(text: str, detected_lang: str, sarvam_key: str) -> str:
    """Translate English AI response back to the user's detected language."""
    if detected_lang in ("en-IN", "en"):
        return text
    if not sarvam_key:
        return text
    try:
        headers = {
            "API-Subscription-Key": sarvam_key,
            "Content-Type": "application/json",
        }
        payload = {
            "source_language_code": "en-IN",
            "target_language_code": detected_lang,
            "speaker_gender": "Male",
            "mode": "formal",
            "model": "mayura:v1",
            "enable_preprocessing": True,
            "input": text,
        }
        resp = requests.post(SARVAM_TRANSLATE_URL, json=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            for key in ("output", "translation", "text", "translated_text"):
                if key in data and isinstance(data[key], str):
                    return data[key]
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
    return text


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinTalk API"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return an AI loan advisory response.
    Language detection + translation are applied automatically.
    """
    if not request.googleApiKey:
        raise HTTPException(status_code=400, detail="Google API key is required")

    # Detect language of the incoming message
    detected_lang, lang_name = _detect_language(request.message)

    # Build user profile dict for the system prompt
    user_profile: Dict[str, Any] = {}
    if request.finCard:
        user_profile = {
            "Full Name": request.finCard.fullName,
            "Age": request.finCard.age,
            "Occupation": request.finCard.occupation,
            "Employment Type": request.finCard.employmentType,
            "Location": request.finCard.location,
            "Monthly Income": request.finCard.monthlyIncome,
            "Credit Score": request.finCard.creditScore,
            "Monthly Expenses": request.finCard.monthlyExpenses,
            "Monthly EMI": request.finCard.monthlyEmi,
            "Amount Outstanding": request.finCard.amountOutstanding,
            "Credit Card Dues": request.finCard.creditCardDues,
        }

    # Create enhanced prompt (system instructions + language constraint + user message)
    enhanced_prompt = (
        f"{_get_loan_advisor_prompt(user_profile)}\n\n"
        f"Please respond strictly in {lang_name}. Do not switch languages.\n\n"
        f"User: {request.message}"
    )

    # Gemini requires role to be 'user' or 'model' (not 'assistant')
    history = [
        genai_types.Content(
            role="model" if msg.role == "assistant" else "user",
            parts=[genai_types.Part.from_text(text=msg.content)],
        )
        for msg in request.chatHistory
    ]

    try:
        client = genai.Client(api_key=request.googleApiKey)
        chat = client.chats.create(
            model="gemini-2.0-flash",
            history=history,
        )
        response = chat.send_message(enhanced_prompt)
        full_response = response.text

        # Translate back to user's language if needed
        final_text = _translate_to_target(full_response, detected_lang, request.sarvamApiKey)

        return ChatResponse(response=final_text, detectedLanguage=detected_lang)

    except Exception as e:
        logger.error(f"Chat generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI response failed: {str(e)}")


@app.post("/api/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    sarvamApiKey: str = Form(...),
    language: str = Form(default="unknown"),
):
    """
    Transcribe uploaded audio using Sarvam AI speech-to-text.
    Accepts WAV, MP3, OGG, M4A.
    Returns: { "text": "...", "detectedLanguage": "hi-IN" }
    """
    if not sarvamApiKey:
        raise HTTPException(status_code=400, detail="Sarvam API key is required")

    audio_bytes = await audio.read()
    if len(audio_bytes) < 1000:
        raise HTTPException(status_code=400, detail="Audio file is too small or empty")

    # Write to a temp file for Sarvam API
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f, "audio/wav")}
            data = {
                "model": "saarika:v2",
                "language_code": language if language != "unknown" else "unknown",
                "with_timestamps": "false",
                "with_diarization": "false",
                "num_speakers": "1",
            }
            headers = {
                "Accept": "application/json",
                "API-Subscription-Key": sarvamApiKey,
            }
            resp = requests.post(SARVAM_STT_URL, files=files, data=data, headers=headers, timeout=60)

        if resp.status_code != 200:
            logger.error(f"STT failed: {resp.status_code} {resp.text[:200]}")
            raise HTTPException(status_code=502, detail="Speech-to-text failed")

        payload = resp.json()
        transcript = ""
        for key in ("text", "transcript", "output"):
            if key in payload and isinstance(payload[key], str):
                transcript = payload[key].strip()
                break

        if not transcript:
            raise HTTPException(status_code=422, detail="Could not transcribe audio")

        detected, _ = _detect_language(transcript)
        return {"text": transcript, "detectedLanguage": detected}

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.post("/api/tts")
async def text_to_speech(
    text: str = Form(...),
    sarvamApiKey: str = Form(...),
    language: str = Form(default="en-IN"),
):
    """
    Convert text to speech using Sarvam AI TTS.
    Returns raw audio/wav binary.

    Note: Frontend sends JSON body, so we also support JSON via a Pydantic model below.
    """
    return await _do_tts(text, sarvamApiKey, language)


class TTSRequest(BaseModel):
    text: str
    sarvamApiKey: str
    language: str = "en-IN"


@app.post("/api/tts/json")
async def text_to_speech_json(req: TTSRequest):
    """JSON body variant (used by the frontend Axios client)."""
    return await _do_tts(req.text, req.sarvamApiKey, req.language)


async def _do_tts(text: str, sarvam_key: str, language: str) -> Response:
    if not sarvam_key:
        raise HTTPException(status_code=400, detail="Sarvam API key is required")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    # Normalize language code
    if len(language) == 2:
        language = LANG_CODE_MAP.get(language, "en-IN")
    if language not in SPEAKER_MAP:
        language = "en-IN"

    speaker = SPEAKER_MAP[language]
    headers = {
        "API-Subscription-Key": sarvam_key,
        "Accept": "audio/wav",
        "Content-Type": "application/json",
    }
    payload = {
        "input": text[:400],  # Sarvam TTS chunk limit
        "language_code": language,
        "speaker": speaker,
        "format": "wav",
        "model": "saarika:v2",
    }

    try:
        resp = requests.post(SARVAM_TTS_URL, headers=headers, json=payload, timeout=60)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS request failed: {e}")

    if resp.status_code == 200:
        content_type = resp.headers.get("Content-Type", "")
        if content_type.startswith("audio"):
            return Response(content=resp.content, media_type="audio/wav")

        # JSON response with base64 audio
        import base64
        data = resp.json()
        audio_b64 = data.get("audio") or data.get("audioContent")
        if audio_b64:
            audio_bytes = base64.b64decode(audio_b64)
            return Response(content=audio_bytes, media_type="audio/wav")

    logger.error(f"TTS failed: {resp.status_code} {resp.text[:200]}")
    raise HTTPException(status_code=502, detail="Text-to-speech failed")
