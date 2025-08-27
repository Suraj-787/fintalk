import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add pages directory to Python path to import from main.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))

st.set_page_config(page_title="FinTalk Home", page_icon="💳", layout="wide")

# Hide Streamlit's default file browser in sidebar
st.markdown("""
<style>
    .css-1d391kg {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    .stDeployButton {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNavItems"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Initialize API keys - check .env first, then session state
if "api_key" not in st.session_state:
    # Try to get from environment first
    env_google_key = os.getenv("GOOGLE_API_KEY", "").strip()
    st.session_state["api_key"] = env_google_key if env_google_key else ""

if "sarvam_api_key" not in st.session_state:
    # Try to get from environment first
    env_sarvam_key = os.getenv("SARVAM_API_KEY", "").strip()
    st.session_state["sarvam_api_key"] = env_sarvam_key if env_sarvam_key else ""

# Initialize override states
if "override_google" not in st.session_state:
    st.session_state["override_google"] = False
if "override_sarvam" not in st.session_state:
    st.session_state["override_sarvam"] = False

# Check if .env file exists and show status
env_file_exists = os.path.exists(".env")
if env_file_exists:
    env_google_available = bool(os.getenv("GOOGLE_API_KEY", "").strip())
    env_sarvam_available = bool(os.getenv("SARVAM_API_KEY", "").strip())
else:
    env_google_available = False
    env_sarvam_available = False

# Sidebar navigation (custom UI)
with st.sidebar:
    st.title("FinTalk")


    # Small CSS refinement for buttons and badges
    st.markdown(
        """
        <style>
        .nav-btn button {
            width: 100%;
            border-radius: 10px !important;
            padding: 0.6rem 0.8rem !important;
            border: 1px solid rgba(49,51,63,0.2) !important;
        }
        .status-badge {
            display: inline-block; padding: 2px 8px; border-radius: 999px;
            font-size: 0.8rem; margin-right: 6px; border: 1px solid rgba(49,51,63,0.2);
        }
        .ok { background: #e8f5e9; color: #2e7d32; }
        .warn { background: #fff3e0; color: #ef6c00; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize page state
    if 'nav_page' not in st.session_state:
        st.session_state['nav_page'] = "🏠 Home"

    # Navigation buttons
    st.markdown("#### Navigation")
    colA, colB = st.columns(2)
    with colA:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state['nav_page'] = "🏠 Home"
    with colB:
        if st.button("🔑 API Key", key="nav_api", use_container_width=True):
            st.session_state['nav_page'] = "🔑 API Key"
    if st.button("💬 Loan Advisor Chat", key="nav_chat", use_container_width=True):
        st.session_state['nav_page'] = "💬 Loan Advisor Chat"

    # API status badges
    st.markdown("---")
    st.markdown("#### Status")
    google_status = "ok" if st.session_state.get("api_key") else "warn"
    sarvam_status = "ok" if st.session_state.get("sarvam_api_key") else "warn"
    st.markdown(
        f"<span class='status-badge {google_status}'>Google API: {'✅' if google_status=='ok' else '⚠️'}</span>"
        f"<span class='status-badge {sarvam_status}'>Sarvam API: {'✅' if sarvam_status=='ok' else '⚠️'}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("v1.0 • Your personal AI loan advisor")

page = st.session_state['nav_page']

if page == "🏠 Home":
    # Landing Page
    st.title("🏦 Welcome to FinTalk")
    st.markdown("### Your Personal AI-Powered Loan Advisor")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **FinTalk** is an intelligent loan advisory platform that helps you make informed financial decisions. 
        Our AI-powered assistant provides personalized guidance for all your loan and financial needs.
        
        #### 🎯 What FinTalk Offers:
        - **Loan Eligibility Assessment** - Get instant feedback on your loan eligibility
        - **Personalized Financial Advice** - Tailored recommendations based on your profile
        - **Application Guidance** - Step-by-step help with loan applications
        - **Financial Literacy** - Learn about credit, debt management, and savings
        - **Multi-language Support** - Chat in your preferred language
        - **Voice & Text Chat** - Communicate via text or voice messages
        
        #### 🚀 Getting Started:
        1. **Set up your API Key** - Enter your Google API key in the API Key section
        2. **Create your FinCard** - Fill out your financial profile for personalized advice
        3. **Start Chatting** - Ask questions about loans, credit, and financial planning
        """)
    
    with col2:
        # st.image("https://via.placeholder.com/300x400/1f77b4/white?text=FinTalk+Logo", caption="FinTalk - Your Financial Companion")
        
        # Quick stats or features
        st.markdown("""
        #### 📊 App Features:
        - 🤖 AI-Powered Responses
        - 🗣️ Voice Recognition
        - 🌐 Multi-language Support
        - 📱 User-Friendly Interface
        - 💳 Personal FinCard Profile
        """)
    
    # Feature highlights
    st.markdown("---")
    st.markdown("### 🌟 Key Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        #### 🎯 Smart Loan Matching
        Get matched with the best loan options based on your financial profile and needs.
        """)
    
    with feature_col2:
        st.markdown("""
        #### 📈 Financial Planning
        Receive personalized advice on improving your credit score and financial health.
        """)
    
    with feature_col3:
        st.markdown("""
        #### 🔒 Secure & Private
        Your financial information is kept secure and private throughout your journey.
        """)
    
    st.markdown("---")
    st.info("💡 **Ready to get started?** Use the sidebar to navigate to the API Key setup, then head to the Loan Advisor Chat!")

elif page == "🔑 API Key":
    st.title("🔑 API Key Setup")
    st.markdown("### Configure your API Keys to enable AI-powered assistance")
    
    # Show environment status
    if env_file_exists:
        st.info("📁 `.env` file detected in your project directory")
        if env_google_available:
            st.success("✅ Google API Key found in `.env` file")
        if env_sarvam_available:
            st.success("✅ Sarvam API Key found in `.env` file")
        if env_google_available and env_sarvam_available:
            st.success("🎉 All API keys are configured via `.env` file! You can start using the chat immediately.")
        elif env_google_available or env_sarvam_available:
            st.warning("⚠️ Some API keys are missing from `.env` file. Configure them below.")
    else:
        st.warning("📁 No `.env` file found. You can create one or configure keys below.")
        with st.expander("💡 How to create a `.env` file"):
            st.markdown("""
            Create a `.env` file in your project root directory with the following content:
            
            ```
            GOOGLE_API_KEY=your_google_api_key_here
            SARVAM_API_KEY=your_sarvam_api_key_here
            ```
            
            This way, your API keys will be loaded automatically when the app starts.
            """)
    
    st.markdown("""
    #### API Key Sources:
    
    **Google API Key (Required for Chat):**
    1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Sign in with your Google account
    3. Create a new API key
    4. Add it to `.env` file or enter below
    
    **Sarvam API Key (Required for Audio Features):**
    1. Visit [Sarvam AI](https://www.sarvam.ai/)
    2. Sign up and get your API key
    3. Add it to `.env` file or enter below
    """)
    
    # Google API Key
    st.subheader("Google API Key")
    if env_google_available:
        st.success("✅ Google API Key is loaded from `.env` file")
        if st.button("🔄 Override with manual input", key="override_google"):
            st.session_state["override_google"] = True
        
        if st.session_state.get("override_google", False):
            google_api_key_input = st.text_input("Google API Key (Override)", type="password", value="", help="This will override the .env value for this session only")
            col_g1, col_g2 = st.columns([1, 1])
            with col_g1:
                if st.button("Save Override", key="save_google_override"):
                    if google_api_key_input.strip():
                        st.session_state["api_key"] = google_api_key_input.strip()
                        st.success("✅ Google API Key overridden for this session!")
                    else:
                        st.error("❌ Please enter a valid Google API key.")
            with col_g2:
                if st.button("Cancel Override", key="cancel_google_override"):
                    st.session_state["override_google"] = False
                    st.session_state["api_key"] = os.getenv("GOOGLE_API_KEY", "").strip()
                    st.rerun()
    else:
        google_api_key_input = st.text_input("Google API Key", type="password", value=st.session_state.get("api_key", "") if not env_google_available else "", help="Enter your Google API key here")
        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            save_google = st.button("Save Google API Key")
        with col_g2:
            clear_google = st.button("Clear Google API Key")

        if save_google:
            if google_api_key_input.strip():
                st.session_state["api_key"] = google_api_key_input.strip()
                st.success("✅ Google API Key saved successfully!")
            else:
                st.error("❌ Please enter a valid Google API key.")
        if clear_google:
            st.session_state["api_key"] = ""
            st.info("🧹 Google API Key cleared for this session.")
    
    # Sarvam API Key
    st.subheader("Sarvam AI API Key (for Audio Features)")
    if env_sarvam_available:
        st.success("✅ Sarvam API Key is loaded from `.env` file")
        if st.button("🔄 Override with manual input", key="override_sarvam"):
            st.session_state["override_sarvam"] = True
        
        if st.session_state.get("override_sarvam", False):
            sarvam_api_key_input = st.text_input("Sarvam API Key (Override)", type="password", value="", help="This will override the .env value for this session only")
            col_s1, col_s2 = st.columns([1, 1])
            with col_s1:
                if st.button("Save Override", key="save_sarvam_override"):
                    if sarvam_api_key_input.strip():
                        st.session_state["sarvam_api_key"] = sarvam_api_key_input.strip()
                        st.success("✅ Sarvam API Key overridden for this session!")
                    else:
                        st.error("❌ Please enter a valid Sarvam API key.")
            with col_s2:
                if st.button("Cancel Override", key="cancel_sarvam_override"):
                    st.session_state["override_sarvam"] = False
                    st.session_state["sarvam_api_key"] = os.getenv("SARVAM_API_KEY", "").strip()
                    st.rerun()
    else:
        sarvam_api_key_input = st.text_input("Sarvam API Key", type="password", value=st.session_state.get("sarvam_api_key", "") if not env_sarvam_available else "", help="Enter your Sarvam API key for audio features")
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            save_sarvam = st.button("Save Sarvam API Key")
        with col_s2:
            clear_sarvam = st.button("Clear Sarvam API Key")

        if save_sarvam:
            if sarvam_api_key_input.strip():
                st.session_state["sarvam_api_key"] = sarvam_api_key_input.strip()
                st.success("✅ Sarvam API Key saved successfully!")
            else:
                st.error("❌ Please enter a valid Sarvam API key.")
        if clear_sarvam:
            st.session_state["sarvam_api_key"] = ""
            st.info("🧹 Sarvam API Key cleared for this session.")
    
    # Status display
    st.markdown("---")
    current_google_key = st.session_state.get("api_key", "")
    current_sarvam_key = st.session_state.get("sarvam_api_key", "")
    
    if current_google_key:
        source = "from .env file" if env_google_available and not st.session_state.get("override_google", False) else "from manual input"
        st.success(f"🔑 Google API Key is configured ({source}). Chat features are ready!")
    else:
        st.warning("⚠️ Please configure your Google API key to enable chat functionality.")
    
    if current_sarvam_key:
        source = "from .env file" if env_sarvam_available and not st.session_state.get("override_sarvam", False) else "from manual input"
        st.success(f"🎤 Sarvam API Key is configured ({source}). Audio features are ready!")
    else:
        st.warning("⚠️ Please configure your Sarvam API key to enable audio features (voice recording and text-to-speech).")

elif page == "💬 Loan Advisor Chat":
    if not st.session_state["api_key"]:
        st.title("💬 Loan Advisor Chat")
        st.warning("🔑 Please set up your Google API Key first!")
        st.markdown("Go to the **API Key** page to configure your Google API key before using the chat feature.")
        
        if st.button("🔑 Go to API Key Setup"):
            st.session_state['nav_page'] = "🔑 API Key"
            st.rerun()
    else:
        # Import and run the main chat functionality
        try:
            from pages.chat import main, sidebar_fincard
            main()
            sidebar_fincard()
        except ImportError as e:
            st.error(f"Error importing chat functionality: {e}")
            st.info("Make sure all required dependencies are installed.")
