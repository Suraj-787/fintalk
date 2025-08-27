"""
Configuration settings for FinTalk application.
Centralizes all configuration constants and settings.
"""

import os
from typing import Dict, List

# Application Information
APP_NAME = "FinTalk"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Your Personal AI-Powered Loan Advisor"

# File Paths
DATA_FILE = "finCard_data.json"
LOG_FILE = "fintalk.log"

# API Configuration
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash"
SARVAM_STT_MODEL = "saarika:v2"
SARVAM_TTS_MODEL = "saarika:v2"
SARVAM_TRANSLATE_MODEL = "mayura:v1"

# Audio Configuration
DEFAULT_CHUNK_LENGTH = 30  # seconds
DEFAULT_SILENCE_THRESHOLD = 0.1
MIN_AUDIO_SIZE = 1000  # bytes
SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'ogg', 'm4a']

# Text Processing Configuration
DEFAULT_TEXT_CHUNK_SIZE = 400  # characters
MAX_TEXT_CHUNK_SIZE = 500  # characters

# Language Configuration
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "hi": "hi-IN", "bn": "bn-IN", "ta": "ta-IN", "te": "te-IN",
    "mr": "mr-IN", "kn": "kn-IN", "gu": "gu-IN", "ml": "ml-IN",
    "pa": "pa-IN", "ur": "ur-IN", "en": "en-IN",
}

LANGUAGE_DISPLAY_MAP: Dict[str, str] = {
    "hi-IN": "🇮🇳 Hindi", "en-IN": "🇺🇸 English", "bn-IN": "🇧🇩 Bengali",
    "ta-IN": "🇮🇳 Tamil", "te-IN": "🇮🇳 Telugu", "mr-IN": "🇮🇳 Marathi",
    "kn-IN": "🇮🇳 Kannada", "gu-IN": "🇮🇳 Gujarati", "ml-IN": "🇮🇳 Malayalam",
    "pa-IN": "🇮🇳 Punjabi", "ur-IN": "🇵🇰 Urdu"
}

LANGUAGE_NAME_MAP: Dict[str, str] = {
    'hi': 'Hindi', 'en': 'English', 'bn': 'Bengali', 'ta': 'Tamil',
    'te': 'Telugu', 'mr': 'Marathi', 'kn': 'Kannada', 'gu': 'Gujarati',
    'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu'
}

SPEAKER_MAP: Dict[str, str] = {
    "hi-IN": "meera", "en-IN": "meera", "bn-IN": "kabita",
    "ta-IN": "oviya", "te-IN": "kareena", "mr-IN": "sarika",
    "kn-IN": "diya", "gu-IN": "kajal", "ml-IN": "asha",
    "pa-IN": "monica", "ur-IN": "ayesha",
}

# FinCard Configuration
EMPLOYMENT_TYPES: List[str] = ["Salaried", "Self-Employed", "Freelancer", "Unemployed"]
MIN_AGE = 18
MAX_AGE = 100
MIN_CREDIT_SCORE = 300
MAX_CREDIT_SCORE = 900

# Default FinCard Values
DEFAULT_FINCARD: Dict[str, any] = {
    "full_name": "",
    "age": MIN_AGE,
    "occupation": "",
    "employment_type": "Salaried",
    "location": "",
    "monthly_income": 0,
    "credit_score": MIN_CREDIT_SCORE,
    "monthly_expenses": 0,
    "monthly_emi": 0,
    "amount_outstanding": 0,
    "credit_dues": 0,
}

# UI Configuration
SIDEBAR_WIDTH = 300
CHAT_INPUT_HEIGHT = 100
MAX_MESSAGE_LENGTH = 1000

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "no_api_key": "🔑 No Google API Key found!",
    "invalid_audio": "Invalid audio data received",
    "no_audio_data": "No audio data in recording",
    "audio_too_small": "Audio file is too small or empty",
    "transcription_failed": "Could not transcribe audio",
    "conversion_failed": "Failed to convert audio",
    "model_init_failed": "Failed to initialize AI model",
    "fincard_save_failed": "Failed to save FinCard data",
}

# Success Messages
SUCCESS_MESSAGES: Dict[str, str] = {
    "fincard_submitted": "FinCard application submitted successfully!",
    "api_key_saved": "API Key saved successfully!",
    "audio_converted": "Audio converted successfully",
    "transcription_complete": "Audio transcribed successfully",
}

# Help Messages
HELP_MESSAGES: Dict[str, str] = {
    "recording_tips": """💡 Tips for better recording:
- Ensure microphone permissions are granted
- Try a shorter recording
- Speak clearly and avoid background noise""",
    
    "transcription_tips": """💡 Tips for better transcription:
- Speak clearly and at normal pace
- Reduce background noise
- Try recording for at least 2-3 seconds""",
    
    "api_setup": """Please configure your API keys:
1. Create a .env file in your project root
2. Add your API keys
3. Restart the application""",
}

# Environment Variable Names
ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"
ENV_SARVAM_API_KEY = "SARVAM_API_KEY"

# Temporary File Patterns
TEMP_AUDIO_PATTERN = "temp_audio_*"
CHUNK_AUDIO_PATTERN = "chunk_*.wav"
TTS_CHUNK_PATTERN = "tts_chunk_*.wav"
RECORDED_AUDIO_FILE = "recorded_audio.wav"
FINAL_OUTPUT_FILE = "final_output.wav"

def get_env_var(var_name: str, default: str = "") -> str:
    """
    Get environment variable with fallback to default.
    
    Args:
        var_name (str): Environment variable name
        default (str): Default value if not found
        
    Returns:
        str: Environment variable value or default
    """
    return os.getenv(var_name, default).strip()

def is_debug_mode() -> bool:
    """
    Check if application is running in debug mode.
    
    Returns:
        bool: True if in debug mode
    """
    return get_env_var("DEBUG", "false").lower() in ("true", "1", "yes")
