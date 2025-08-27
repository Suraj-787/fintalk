"""
Main application module for FinTalk loan advisor chat functionality.
Handles user interactions, audio processing, and AI-powered responses.
"""

import streamlit as st
import os
import json
import logging
from dotenv import load_dotenv
import langid
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import mic_recorder, use fallback if not available
try:
    from streamlit_mic_recorder import mic_recorder
    MIC_RECORDER_AVAILABLE = True
except ImportError:
    MIC_RECORDER_AVAILABLE = False
    logger.warning("streamlit-mic-recorder not available. Audio recording disabled.")

# Import modularized functions
from .audio_utils import convert_webm_to_wav, process_long_audio, merge_audio
from .api_utils import audio_to_text, text_to_speech, translate_response_to_detectLang
from .model_utils import init_model

# Load environment variables
load_dotenv()

# Configuration
DATA_FILE = "finCard_data.json"
LANGUAGE_DISPLAY_MAP = {
    "hi-IN": "🇮🇳 Hindi", "en-IN": "🇺🇸 English", "bn-IN": "🇧🇩 Bengali",
    "ta-IN": "🇮🇳 Tamil", "te-IN": "🇮🇳 Telugu", "mr-IN": "🇮🇳 Marathi",
    "kn-IN": "🇮🇳 Kannada", "gu-IN": "🇮🇳 Gujarati", "ml-IN": "🇮🇳 Malayalam",
    "pa-IN": "🇮🇳 Punjabi", "ur-IN": "🇵🇰 Urdu"
}

LANGUAGE_NAME_MAP = {
    'hi': 'Hindi', 'en': 'English', 'bn': 'Bengali', 'ta': 'Tamil',
    'te': 'Telugu', 'mr': 'Marathi', 'kn': 'Kannada', 'gu': 'Gujarati',
    'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu'
}

LANG_CODE_MAPPING = {
    'hi': 'hi-IN', 'en': 'en-IN', 'bn': 'bn-IN', 'ta': 'ta-IN', 
    'te': 'te-IN', 'mr': 'mr-IN', 'kn': 'kn-IN', 'gu': 'gu-IN', 
    'ml': 'ml-IN', 'pa': 'pa-IN', 'ur': 'ur-IN'
}


def get_api_key() -> str:
    """
    Get Google API key from session state or environment variable.
    
    Returns:
        str: API key or empty string if not found
    """
    session_key = st.session_state.get("api_key", "")
    if session_key:
        return session_key
    
    # Fallback to environment variable
    env_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if env_key:
        st.session_state["api_key"] = env_key
        return env_key
    
    return ""


def get_sarvam_api_key() -> str:
    """
    Get Sarvam API key from session state or environment variable.
    
    Returns:
        str: API key or empty string if not found
    """
    session_key = st.session_state.get("sarvam_api_key", "")
    if session_key:
        return session_key
    
    # Fallback to environment variable
    env_key = os.getenv("SARVAM_API_KEY", "").strip()
    if env_key:
        st.session_state["sarvam_api_key"] = env_key
        return env_key
    
    return ""


def load_fincard_data() -> list:
    """
    Load FinCard data from JSON file.
    
    Returns:
        list: List of FinCard entries or empty list if file doesn't exist
    """
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in FinCard data file")
            return []
    return []


def save_fincard_data(data: list) -> None:
    """
    Save FinCard data to JSON file.
    
    Args:
        data (list): FinCard data to save
    """
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logger.error(f"Failed to save FinCard data: {e}")
        st.error("Failed to save FinCard data")


def get_loan_advisor_prompt(user_profile: Dict[str, Any]) -> str:
    """
    Generate the loan advisor system prompt with user profile.
    
    Args:
        user_profile (Dict[str, Any]): User's financial profile
        
    Returns:
        str: Formatted system prompt
    """
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


def detect_and_normalize_language(text: str) -> tuple[str, str]:
    """
    Detect language and normalize to supported format.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        tuple[str, str]: (normalized_lang_code, language_name)
    """
    try:
        detected_lang = langid.classify(text)[0]
        normalized_lang = LANG_CODE_MAPPING.get(detected_lang, 'en-IN')
        lang_name = LANGUAGE_NAME_MAP.get(detected_lang, 'English')
        return normalized_lang, lang_name
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return 'en-IN', 'English'


def initialize_chat_session(api_key: str) -> None:
    """
    Initialize chat session and conversation history.
    
    Args:
        api_key (str): Google API key for model initialization
    """
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help with your loan needs today?"}
        ]
    
    if ("conversation" not in st.session_state or 
        st.session_state.get("api_key_for_model") != api_key):
        try:
            chat_history = [
                {"role": msg["role"], "parts": [{"text": msg["content"]}]}
                for msg in st.session_state.messages
            ]
            model = init_model(api_key)
            st.session_state.conversation = model.start_chat(history=chat_history)
            st.session_state["api_key_for_model"] = api_key
        except Exception as e:
            logger.error(f"Failed to initialize chat session: {e}")
            st.error("Failed to initialize AI model. Please check your API key.")


def display_chat_history() -> None:
    """Display chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    """Main chat application interface."""
    st.title("Loan Advisor AI")

    # Get API key and validate
    api_key = get_api_key()
    if not api_key:
        _display_api_key_setup_instructions()
        return

    # Load user profile
    fincard_data = load_fincard_data()
    user_profile = fincard_data[-1] if fincard_data else {}

    # Initialize chat session
    initialize_chat_session(api_key)

    # Display chat history
    display_chat_history()

    # Input section
    _render_input_section(user_profile)


def _display_api_key_setup_instructions() -> None:
    """Display instructions for API key setup."""
    st.warning("🔑 No Google API Key found!")
    st.info("Please configure your Google API Key in one of the following ways:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Option 1: Using .env file (Recommended)**
        1. Create a `.env` file in your project root
        2. Add: `GOOGLE_API_KEY=your_api_key_here`
        3. Restart the application
        """)
    
    with col2:
        st.markdown("""
        **Option 2: Using the API Key page**
        1. Go to the API Key page in the sidebar
        2. Enter your Google API key manually
        3. Click Save
        """)
    
    if st.button("🔑 Go to API Key Setup"):
        st.info("Please use the sidebar navigation to go to the API Key page.")


def _render_input_section(user_profile: Dict[str, Any]) -> None:
    """Render the chat input section with text and audio options."""
    st.markdown("---")
    col1, col2 = st.columns([0.75, 0.25])
    
    with col1:
        prompt = st.chat_input("Ask about loans or financial advice...", key="chat_input")
    
    with col2:
        audio = _render_audio_input_section()

    # Handle inputs
    if prompt:
        handle_user_input(prompt, user_profile)
    
    if audio:
        handle_audio_input(audio, user_profile)


def _render_audio_input_section() -> Optional[dict]:
    """
    Render audio input section and return audio data if available.
    
    Returns:
        Optional[dict]: Audio data dictionary or None
    """
    sarvam_key = get_sarvam_api_key()
    if not sarvam_key:
        st.info("🎤 **Audio Disabled**")
        st.caption("Configure Sarvam API key to enable audio features")
        if os.path.exists(".env"):
            st.caption("💡 Add SARVAM_API_KEY to your .env file")
        else:
            st.caption("💡 Configure in API Key page or create .env file")
        return None

    st.markdown("**🎤 Audio Input**")
    
    if MIC_RECORDER_AVAILABLE:
        audio_method = st.radio(
            "Choose method:", ["🎤 Record", "📁 Upload"], 
            horizontal=True, key="audio_method"
        )
        
        if audio_method == "🎤 Record":
            return _handle_microphone_recording()
        else:
            return _handle_audio_upload()
    else:
        st.info("🎤 Mic recorder unavailable")
        return _handle_audio_upload()


def _handle_microphone_recording() -> Optional[dict]:
    """Handle microphone recording."""
    try:
        audio = mic_recorder(
            start_prompt="▶️ Start", 
            stop_prompt="⏹️ Stop", 
            key="recorder",
            format="wav",
            use_container_width=True
        )
        return audio
    except Exception as e:
        st.error(f"Recorder error: {e}")
        return None


def _handle_audio_upload() -> Optional[dict]:
    """Handle audio file upload."""
    uploaded_audio = st.file_uploader(
        "Upload audio file", 
        type=['wav', 'mp3', 'ogg', 'm4a'],
        key="audio_upload",
        help="Upload a WAV, MP3, OGG, or M4A file"
    )
    
    if uploaded_audio is not None:
        return {'bytes': uploaded_audio.read()}
    return None


def handle_user_input(user_text: str, user_profile: Dict[str, Any]) -> None:
    """
    Handle text input from user.
    
    Args:
        user_text (str): User's text input
        user_profile (Dict[str, Any]): User's financial profile
    """
    # Detect language
    detected_lang, target_lang_name = detect_and_normalize_language(user_text)
    st.session_state["original_language"] = detected_lang
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    # Generate AI response
    _generate_ai_response(user_text, user_profile, target_lang_name, detected_lang)


def handle_audio_input(audio: dict, user_profile: Dict[str, Any]) -> None:
    """
    Handle audio input from user.
    
    Args:
        audio (dict): Audio data dictionary
        user_profile (Dict[str, Any]): User's financial profile
    """
    sarvam_api_key = get_sarvam_api_key()
    if not sarvam_api_key:
        st.warning("🎤 Audio features require Sarvam API key.")
        return
    
    # Validate audio input
    if not _validate_audio_input(audio):
        return
    
    # Set environment variable for audio processing
    os.environ["SARVAM_API_KEY"] = sarvam_api_key
    
    try:
        transcript = _process_audio_to_text(audio['bytes'])
        if not transcript:
            return
            
        # Detect language and process
        detected_lang, target_lang_name = detect_and_normalize_language(transcript)
        st.session_state["original_language"] = detected_lang
        
        # Add to chat
        st.session_state.messages.append({"role": "user", "content": transcript})
        
        with st.chat_message("user"):
            st.markdown(transcript)
        
        # Generate response with audio
        _generate_ai_response_with_audio(transcript, user_profile, target_lang_name, detected_lang)
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        st.error(f"Audio processing error: {str(e)}")
        st.info("Please try again or use text input instead.")


def _validate_audio_input(audio: dict) -> bool:
    """Validate audio input data."""
    if not audio or not isinstance(audio, dict):
        st.error("Invalid audio data received")
        return False
        
    if 'bytes' not in audio or not audio['bytes']:
        st.error("No audio data in recording")
        return False
        
    return True


def _process_audio_to_text(audio_bytes: bytes) -> Optional[str]:
    """Process audio bytes to text transcript."""
    with st.spinner("🎤 Converting audio..."):
        wav_audio = convert_webm_to_wav(audio_bytes)
        
    if not wav_audio:
        st.error("Failed to convert audio. Please try recording again.")
        _display_audio_tips()
        return None

    save_path = "recorded_audio.wav"
    try:
        with open(save_path, "wb") as f:
            f.write(wav_audio)

        if not (os.path.exists(save_path) and os.path.getsize(save_path) > 1000):
            st.error("Audio file is too small or empty. Please try recording again.")
            return None

        with st.spinner("🎤 Processing your voice message..."):
            transcript = process_long_audio(save_path)
            
        if not transcript or len(transcript.strip()) < 2:
            st.error("Could not transcribe audio. Please try speaking more clearly.")
            _display_transcription_tips()
            return None
            
        st.success(f"🎤 Heard: {transcript}")
        return transcript
        
    finally:
        # Clean up
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
        except:
            pass


def _display_audio_tips() -> None:
    """Display tips for better audio recording."""
    st.info("💡 Tips for better recording:")
    st.info("- Ensure microphone permissions are granted")
    st.info("- Try a shorter recording")
    st.info("- Speak clearly and avoid background noise")


def _display_transcription_tips() -> None:
    """Display tips for better transcription."""
    st.info("💡 Tips for better transcription:")
    st.info("- Speak clearly and at normal pace")
    st.info("- Reduce background noise")
    st.info("- Try recording for at least 2-3 seconds")


def _generate_ai_response(user_text: str, user_profile: Dict[str, Any], 
                         target_lang_name: str, detected_lang: str) -> None:
    """Generate AI response for text input."""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            enhanced_prompt = _create_enhanced_prompt(user_text, user_profile, target_lang_name)
            response = st.session_state.conversation.send_message(enhanced_prompt, stream=True)

            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            # Translate response if needed
            final_text = translate_response_to_detectLang(full_response, detected_lang)
            message_placeholder.markdown(final_text)
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            message_placeholder.markdown(f"Error: {str(e)}")
            st.error("Please check your API key and connection.")


def _generate_ai_response_with_audio(transcript: str, user_profile: Dict[str, Any], 
                                   target_lang_name: str, detected_lang: str) -> None:
    """Generate AI response with audio output."""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Thinking...")
        
        try:
            enhanced_prompt = _create_enhanced_prompt(transcript, user_profile, target_lang_name)
            response = st.session_state.conversation.send_message(enhanced_prompt, stream=True)

            full_response = "".join(chunk.text for chunk in response if chunk.text)
            final_text = translate_response_to_detectLang(full_response, detected_lang)

            message_placeholder.markdown(final_text)
            st.session_state.messages.append({"role": "assistant", "content": final_text})

            # Generate audio response
            _generate_audio_response(final_text, detected_lang)

        except Exception as e:
            logger.error(f"AI response with audio failed: {e}")
            message_placeholder.markdown(f"❌ Error: {str(e)}")
            st.error("Please check your API keys and connection.")


def _create_enhanced_prompt(user_input: str, user_profile: Dict[str, Any], 
                          target_lang_name: str) -> str:
    """Create enhanced prompt for AI model."""
    return (
        f"{get_loan_advisor_prompt(user_profile)}\n\n"
        f"Please respond strictly in {target_lang_name}. Do not switch languages.\n\n"
        f"User: {user_input}"
    )


def _generate_audio_response(final_text: str, original_lang: str) -> None:
    """Generate audio response for the text."""
    with st.spinner("🔊 Generating audio response..."):
        audio_files = text_to_speech(final_text, target_language=original_lang)
        if audio_files:
            merge_audio(audio_files)
            if os.path.exists("final_output.wav"):
                st.audio("final_output.wav", format="audio/wav")
            else:
                st.warning("Audio response generation failed.")
        else:
            st.info("Text-to-speech not available, but you can read the response above.")


def sidebar_fincard() -> None:
    """Render the FinCard sidebar form."""
    st.sidebar.title("Settings")

    fincard_data = load_fincard_data()
    
    # Initialize form state
    if "finCard_form" not in st.session_state:
        st.session_state["finCard_form"] = {
            "full_name": "", "age": 18, "occupation": "",
            "employment_type": "Salaried", "location": "",
            "monthly_income": 0, "credit_score": 300,
            "monthly_expenses": 0, "monthly_emi": 0,
            "amount_outstanding": 0, "credit_dues": 0,
        }

    # Render form
    _render_fincard_form()
    
    # Display current FinCard data
    _display_current_fincard(fincard_data)


def _render_fincard_form() -> None:
    """Render the FinCard input form."""
    with st.sidebar.form("finCard"):
        st.write("💳 **FinCard Details**")
        form = st.session_state["finCard_form"]

        # Form fields
        full_name = st.text_input("Full Name", form["full_name"])
        age = st.number_input("Age", min_value=18, max_value=100, value=form["age"])
        occupation = st.text_input("Occupation", form["occupation"])
        
        employment_type = st.selectbox(
            "Employment Type",
            ["Salaried", "Self-Employed", "Freelancer", "Unemployed"],
            index=["Salaried", "Self-Employed", "Freelancer", "Unemployed"].index(form["employment_type"])
        )
        
        location = st.text_input("Location", form["location"])
        monthly_income = st.number_input("Monthly Income (in ₹)", min_value=0, value=form["monthly_income"])
        credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=form["credit_score"])
        monthly_expenses = st.number_input("Monthly Expenses (in ₹)", min_value=0, value=form["monthly_expenses"])
        monthly_emi = st.number_input("Monthly EMI (in ₹)", min_value=0, value=form["monthly_emi"])
        amount_outstanding = st.number_input("Amount Outstanding (in ₹)", min_value=0, value=form["amount_outstanding"])
        credit_dues = st.number_input("Credit Card Dues (in ₹)", min_value=0, value=form["credit_dues"])

        submitted = st.form_submit_button("Submit")

        if submitted:
            _handle_fincard_submission(
                full_name, age, occupation, employment_type, location,
                monthly_income, credit_score, monthly_expenses, monthly_emi,
                amount_outstanding, credit_dues
            )


def _handle_fincard_submission(full_name: str, age: int, occupation: str, 
                             employment_type: str, location: str, monthly_income: int,
                             credit_score: int, monthly_expenses: int, monthly_emi: int,
                             amount_outstanding: int, credit_dues: int) -> None:
    """Handle FinCard form submission."""
    form_entry = {
        "Full Name": full_name, "Age": age, "Occupation": occupation,
        "Employment Type": employment_type, "Location": location,
        "Monthly Income": monthly_income, "Credit Score": credit_score,
        "Monthly Expenses": monthly_expenses, "Monthly EMI": monthly_emi,
        "Amount Outstanding": amount_outstanding, "Credit Card Dues": credit_dues,
    }
    
    fincard_data = load_fincard_data()
    fincard_data.append(form_entry)
    save_fincard_data(fincard_data)

    # Update form state
    st.session_state["finCard_form"] = {
        "full_name": full_name, "age": age, "occupation": occupation,
        "employment_type": employment_type, "location": location,
        "monthly_income": monthly_income, "credit_score": credit_score,
        "monthly_expenses": monthly_expenses, "monthly_emi": monthly_emi,
        "amount_outstanding": amount_outstanding, "credit_dues": credit_dues,
    }
    
    st.sidebar.success("FinCard application submitted successfully!")


def _display_current_fincard(fincard_data: list) -> None:
    """Display current FinCard information."""
    if fincard_data:
        latest_entry = fincard_data[-1]
        st.sidebar.markdown("---")
        st.sidebar.subheader("💳 Your FinCard")
        for key, value in latest_entry.items():
            st.sidebar.markdown(f"**{key}:** {value}")
    else:
        st.sidebar.info("No FinCard data available. Submit your application to see details.")


# Main execution
if __name__ == "__main__":
    main()
    sidebar_fincard()
