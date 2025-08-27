"""
API utilities for FinTalk application.
Handles interactions with Sarvam AI APIs for speech-to-text, text-to-speech, and translation.
"""

import os
import json
import base64
import uuid
from typing import List, Optional, Tuple
import logging

import requests
from langdetect import detect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Endpoints
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"

# Language and speaker mappings
LANG_CODE_MAP = {
    "hi": "hi-IN", "bn": "bn-IN", "ta": "ta-IN", "te": "te-IN",
    "mr": "mr-IN", "kn": "kn-IN", "gu": "gu-IN", "ml": "ml-IN",
    "pa": "pa-IN", "ur": "ur-IN", "en": "en-IN",
}

SPEAKER_MAP = {
    "hi-IN": "meera", "en-IN": "meera", "bn-IN": "kabita",
    "ta-IN": "oviya", "te-IN": "kareena", "mr-IN": "sarika",
    "kn-IN": "diya", "gu-IN": "kajal", "ml-IN": "asha",
    "pa-IN": "monica", "ur-IN": "ayesha",
}


def audio_to_text(audio_file_path: str) -> str:
    """
    Transcribe an audio file to text using Sarvam STT.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text (empty string on failure)
    """
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        logger.error("SARVAM_API_KEY not found!")
        return ""

    if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
        logger.error(f"Audio file {audio_file_path} not found or empty!")
        return ""

    try:
        with open(audio_file_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_file_path), audio_file, "audio/wav")}
            data = {
                "model": "saarika:v2",
                "language_code": "unknown",
                "with_timestamps": "false",
                "with_diarization": "false",
                "num_speakers": "1",
            }
            headers = {
                "Accept": "application/json",
                "API-Subscription-Key": api_key,
            }
            
            response = requests.post(
                SARVAM_STT_URL, files=files, data=data, 
                headers=headers, timeout=60
            )
            
            if response.status_code == 200:
                return _extract_transcript_from_response(response.json())
            else:
                logger.error(f"STT failed: {response.status_code} - {response.text[:200]}")
                return ""
                
    except Exception as e:
        logger.error(f"Error in audio_to_text: {e}")
        return ""


def _extract_transcript_from_response(payload: dict) -> str:
    """Extract transcript text from API response."""
    # Try common response keys
    for key in ("text", "transcript", "output"):
        if key in payload and isinstance(payload[key], str):
            return payload[key].strip()
    
    # Try nested result structure
    if "result" in payload and isinstance(payload["result"], dict):
        for key in ("text", "transcript"):
            if key in payload["result"]:
                return str(payload["result"][key]).strip()
    
    logger.warning("STT response JSON missing expected keys")
    return ""


def text_to_speech(full_transcript: str, API: Optional[str] = None, 
                  target_language: str = "en-IN") -> List[str]:
    """
    Synthesize speech for the given text using Sarvam TTS.
    
    Args:
        full_transcript (str): Text to convert to speech
        API (Optional[str]): API key override
        target_language (str): Target language code (default: "en-IN")
        
    Returns:
        List[str]: List of WAV filenames created on disk
    """
    api_key = API or os.getenv("SARVAM_API_KEY")
    if not api_key:
        logger.error("SARVAM_API_KEY not found!")
        return []

    # Normalize language and get speaker
    lang_key = _normalize_language_code(target_language)
    speaker = SPEAKER_MAP.get(lang_key, "meera")

    try:
        text_chunks = _split_text_for_tts(full_transcript)
        audio_files = []

        headers = {
            "API-Subscription-Key": api_key,
            "Accept": "audio/wav",
            "Content-Type": "application/json",
        }

        for i, chunk in enumerate(text_chunks):
            audio_file = _synthesize_speech_chunk(chunk, lang_key, speaker, headers, i)
            if audio_file:
                audio_files.append(audio_file)

        return audio_files
        
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        return []


def _normalize_language_code(target_language: str) -> str:
    """Normalize language code to supported format."""
    lang_key = target_language
    if len(lang_key) == 2:
        lang_key = LANG_CODE_MAP.get(lang_key, "en-IN")
    if lang_key not in SPEAKER_MAP:
        lang_key = "en-IN"
    return lang_key


def _split_text_for_tts(text: str, max_length: int = 400) -> List[str]:
    """Split text into chunks for TTS processing."""
    try:
        from .text_utils import split_text
        return split_text(text, max_length)
    except ImportError:
        # Fallback if text_utils not available
        return [text]


def _synthesize_speech_chunk(chunk: str, lang_key: str, speaker: str, 
                           headers: dict, index: int) -> Optional[str]:
    """Synthesize speech for a single text chunk."""
    payload = {
        "input": chunk,
        "language_code": lang_key,
        "speaker": speaker,
        "format": "wav",
        "model": "saarika:v2",
    }
    
    try:
        response = requests.post(
            SARVAM_TTS_URL, headers=headers, 
            data=json.dumps(payload), timeout=60
        )
        
        if response.status_code == 200:
            return _save_audio_response(response, index)
        else:
            return _handle_tts_json_response(response, index)
            
    except Exception as e:
        logger.error(f"TTS chunk {index} error: {e}")
        return None


def _save_audio_response(response: requests.Response, index: int) -> Optional[str]:
    """Save audio response to file."""
    if response.headers.get("Content-Type", "").startswith("audio"):
        out_path = os.path.abspath(f"tts_chunk_{index}_{uuid.uuid4().hex[:6]}.wav")
        with open(out_path, "wb") as f:
            f.write(response.content)
        return out_path
    return None


def _handle_tts_json_response(response: requests.Response, index: int) -> Optional[str]:
    """Handle TTS JSON response with base64 audio."""
    try:
        data = response.json()
        audio_b64 = data.get("audio") or data.get("audioContent")
        if audio_b64:
            audio_bytes = base64.b64decode(audio_b64)
            out_path = os.path.abspath(f"tts_chunk_{index}_{uuid.uuid4().hex[:6]}.wav")
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            return out_path
        else:
            logger.warning(f"TTS unexpected JSON keys: {list(data.keys())}")
            return None
    except Exception:
        logger.error(f"TTS failed: {response.status_code} {response.text[:200]}")
        return None



def translate_to_english(text: str) -> Tuple[str, str]:
    """
    Translate input text to English using Sarvam AI.
    
    Args:
        text (str): Text to translate
        
    Returns:
        Tuple[str, str]: (translated_text, detected_language_code)
        If already English or translation unavailable, returns original text and detected code.
    """
    api_key = os.getenv("SARVAM_API_KEY")
    
    # Detect language
    try:
        detected_lang = detect(text)
    except Exception:
        detected_lang = "en"
    
    detected_lang_code = LANG_CODE_MAP.get(detected_lang, "en-IN")

    if not api_key:
        logger.warning("SARVAM_API_KEY not found, translation disabled")
        return text, detected_lang_code

    # Skip translation if already English
    if detected_lang_code in ("en-IN", "en"):
        return text, "en-IN"

    headers = {
        "API-Subscription-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "source_language_code": detected_lang_code,
        "target_language_code": "en-IN",
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": True,
        "input": text,
    }
    
    try:
        response = requests.post(
            SARVAM_TRANSLATE_URL, json=payload, 
            headers=headers, timeout=60
        )
        
        if response.status_code == 200:
            translated_text = _extract_translation_from_response(response.json())
            return translated_text or text, detected_lang_code
        else:
            logger.error(f"Translation failed: {response.status_code} - {response.text[:200]}")
            return text, detected_lang_code
            
    except Exception as e:
        logger.error(f"Translation exception: {e}")
        return text, detected_lang_code


def translate_response_to_detectLang(response_text: str, detected_lang_code: str) -> str:
    """
    Translate English response back to the user's detected language.
    
    Args:
        response_text (str): Text to translate (assumed to be in English)
        detected_lang_code (str): Target language code
        
    Returns:
        str: Translated text or original if translation fails/unnecessary
    """
    if not response_text:
        return response_text

    # Skip if target is English
    if detected_lang_code in ("en-IN", "en"):
        return response_text

    # Check if text is already in target language
    try:
        resp_lang = detect(response_text)
        if LANG_CODE_MAP.get(resp_lang, resp_lang) == detected_lang_code:
            return response_text
    except Exception:
        pass

    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        logger.warning("SARVAM_API_KEY not found for response translation")
        return response_text

    headers = {
        "API-Subscription-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "source_language_code": "en-IN",
        "target_language_code": detected_lang_code,
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": True,
        "input": response_text,
    }
    
    try:
        response = requests.post(
            SARVAM_TRANSLATE_URL, json=payload, 
            headers=headers, timeout=60
        )
        
        if response.status_code == 200:
            translated_text = _extract_translation_from_response(response.json())
            return translated_text or response_text
        else:
            logger.error(f"Response translation failed: {response.status_code} - {response.text[:200]}")
            return response_text
            
    except Exception as e:
        logger.error(f"Response translation exception: {e}")
        return response_text


def _extract_translation_from_response(data: dict) -> Optional[str]:
    """Extract translated text from API response."""
    # Try common response keys
    for key in ("output", "translation", "text", "translated_text"):
        if key in data and isinstance(data[key], str):
            return data[key]
    
    # Try nested result structure
    if "result" in data and isinstance(data["result"], dict):
        out = data["result"].get("text") or data["result"].get("output")
        if out:
            return str(out)
    
    logger.warning("Translation response missing expected keys")
    return None
