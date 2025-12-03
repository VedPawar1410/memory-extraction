"""
AI Memory & Personality Engine - Streamlit Application

A prototype that extracts structured memory from chat history
and demonstrates personality-based response rewriting.
"""

import os
import streamlit as st
from dotenv import load_dotenv
import json

from memory_engine import MemoryEngine, UserProfile
from personality_engine import PersonalityEngine


# Load environment variables
load_dotenv()


def inject_custom_css():
    """Inject Neo-Brutalist / Playful Pop-Art custom CSS styling."""
    st.markdown("""
    <style>
    /* Import Space Grotesk font */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Global font application */
    * {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    /* Force text color globally for HIGH CONTRAST */
    .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, div, li, label {
        color: #000000 !important;
    }
    
    /* Animated gradient mesh background */
    .stApp {
        background: linear-gradient(
            45deg,
            #FFB3D9 0%,
            #C5B3FF 25%,
            #B3D9FF 50%,
            #FFD1DC 75%,
            #E0BBE4 100%
        );
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Neo-Brutalist Buttons */
    .stButton > button {
        background-color: #FF4B4B !important;
        color: white !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px 0px #000000 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        transition: all 0.1s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 6px 6px 0px 0px #000000 !important;
        background-color: #FF3333 !important;
    }
    
    .stButton > button:active {
        transform: translate(2px, 2px) !important;
        box-shadow: 0px 0px 0px 0px #000000 !important;
    }
    
    /* Primary buttons - different color */
    .stButton > button[kind="primary"] {
        background-color: #6C63FF !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #5A52E8 !important;
    }
    
    /* Text Inputs */
    .stTextInput > div > div > input {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #E0E0E0 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important; /* Fix for Chrome autofill */
        padding: 12px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    /* Placeholder text for inputs */
    .stTextInput > div > div > input::placeholder {
        color: #404040 !important;
        opacity: 1 !important;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: 6px 6px 0px #C0C0C0 !important;
        border-color: #6C63FF !important;
        outline: none !important;
    }
    
    /* Text Areas */
    .stTextArea > div > div > textarea {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #E0E0E0 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important; /* Fix for Chrome autofill */
        padding: 12px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    /* Placeholder text for text areas */
    .stTextArea > div > div > textarea::placeholder {
        color: #404040 !important;
        opacity: 1 !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        box-shadow: 6px 6px 0px #C0C0C0 !important;
        border-color: #6C63FF !important;
        outline: none !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div > div {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #E0E0E0 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Make labels readable and bold */
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Cards / Containers */
    .stExpander {
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        background-color: #FFFDF5 !important;
        box-shadow: 6px 6px 0px #000000 !important;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000000 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 700 !important;
        text-shadow: 3px 3px 0px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #000000 !important;
    }
    
    /* JSON display area */
    .stJson {
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        background-color: #FFFDF5 !important;
        box-shadow: 6px 6px 0px #000000 !important;
        padding: 16px !important;
    }
    
    /* Markdown in columns (for extracted profile) */
    [data-testid="column"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000000 !important;
        padding: 16px !important;
        margin: 4px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #FF4B4B !important;
        border-right-color: #6C63FF !important;
    }
    
    /* Horizontal rule */
    hr {
        border: 2px solid #000000 !important;
        margin: 32px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Default dummy conversation
DEFAULT_CHAT = """User: Hey! I've been thinking about learning Python. I'm a graphic designer based in Portland, and I feel like coding could help me automate some of my work.

AI: That's a great idea! Python is perfect for automation. What kind of tasks do you want to automate?

User: Mostly batch processing images and organizing files. I work with hundreds of photos every week and it's exhausting. Also, I'm a bit anxious about learning to code - I've never been good at math.

AI: Don't worry! Python for automation doesn't require advanced math. It's more about logic and problem-solving. Have you tried any coding before?

User: Not really. I tried JavaScript once but got frustrated and gave up. I prefer visual things, which is why I became a designer in the first place.

AI: That makes sense! Python has great libraries for visual feedback. You might enjoy working with image processing libraries like Pillow or OpenCV.

User: That sounds cool! I usually work late at night because that's when I'm most creative. My cat, Luna, keeps me company during those late coding sessions now.

AI: Night owl programmer with a cat companion - classic! When do you want to start?

User: Maybe this weekend? I'm pretty excited but also nervous. I tend to get overwhelmed easily when learning new things."""


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="AI Memory & Personality Engine",
        page_icon="🧠",
        layout="wide"
    )
    
    # Inject Neo-Brutalist custom CSS
    inject_custom_css()
    
    st.title("🧠 AI Memory & Personality Engine")
    st.markdown("Extract structured memory from conversations and rewrite responses with personality.")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key_input = st.text_input(
            "Google API Key",
            type="password",
            help="Enter your Google Gemini API key (or set in .env file)",
            placeholder="AIza..."
        )
        
        # Strip whitespace and validate input
        api_key_input = api_key_input.strip() if api_key_input else ""
        
        # Use input if provided (and not empty after stripping), otherwise fall back to environment variable
        # IMPORTANT: Never store user-provided API keys in os.environ as it's shared across sessions
        api_key = api_key_input if api_key_input else os.environ.get("GOOGLE_API_KEY")
        
        if api_key_input:
            st.success("✅ API Key set from input!")
        elif api_key:
            st.success("✅ API Key loaded from environment!")
        else:
            st.warning("⚠️ Please enter your Google API Key or set it in .env file")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app demonstrates:
        - 📝 Memory extraction from chat logs
        - 🎭 Personality-based response rewriting
        - 🤖 Powered by Google Gemini
        """)
    
    # Main content area
    if not api_key:
        st.info("👈 Please enter your Google API Key in the sidebar or set it in your .env file to get started.")
        return
    
    # Section 1: Chat History Input
    st.header("1️⃣ Chat History Analysis")
    
    chat_history = st.text_area(
        "Paste Chat History Here",
        value=DEFAULT_CHAT,
        height=300,
        help="Paste a conversation between a user and AI to extract memory"
    )
    
    # Initialize session state for storing extracted memory
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    
    # Analyze button
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("🔍 Analyze User", type="primary", use_container_width=True)
    
    if analyze_button:
        if not chat_history.strip():
            st.error("❌ Please provide a chat history to analyze.")
        else:
            with st.spinner("Analyzing chat history..."):
                try:
                    # Initialize memory engine and extract profile
                    memory_engine = MemoryEngine(api_key=api_key)
                    user_profile = memory_engine.extract_from_chat(chat_history)
                    st.session_state.user_profile = user_profile
                    st.success("✅ Memory extraction complete!")
                except Exception as e:
                    st.error(f"❌ Error during extraction: {str(e)}")
    
    # Display extracted memory
    if st.session_state.user_profile:
        st.subheader("📊 Extracted User Profile")
        
        # Create three columns for the profile data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**👤 Facts**")
            if st.session_state.user_profile.facts:
                for fact in st.session_state.user_profile.facts:
                    st.markdown(f"- {fact}")
            else:
                st.markdown("*None extracted*")
        
        with col2:
            st.markdown("**❤️ Preferences**")
            if st.session_state.user_profile.preferences:
                for pref in st.session_state.user_profile.preferences:
                    st.markdown(f"- {pref}")
            else:
                st.markdown("*None extracted*")
        
        with col3:
            st.markdown("**🎭 Emotional Patterns**")
            if st.session_state.user_profile.emotional_patterns:
                for pattern in st.session_state.user_profile.emotional_patterns:
                    st.markdown(f"- {pattern}")
            else:
                st.markdown("*None extracted*")
        
        # Show JSON view in expander
        with st.expander("📄 View Raw JSON"):
            profile_dict = {
                "facts": st.session_state.user_profile.facts,
                "preferences": st.session_state.user_profile.preferences,
                "emotional_patterns": st.session_state.user_profile.emotional_patterns
            }
            st.json(profile_dict)
    
    # Section 2: Personality Testing
    st.markdown("---")
    st.header("2️⃣ Test Personality Rewriting")
    
    if not st.session_state.user_profile:
        st.info("👆 Please analyze a chat history first to extract user profile.")
    else:
        # Input for generic AI response
        generic_response = st.text_area(
            "Generic AI Response",
            value="I can help you learn programming. Let's start with the basics and work through some examples together. Practice is key to success.",
            height=100,
            help="Enter a generic AI response to transform"
        )
        
        # Persona selection
        col1, col2 = st.columns([2, 3])
        
        with col1:
            persona = st.selectbox(
                "Select Persona",
                options=[
                    "friendly and encouraging",
                    "professional and formal",
                    "casual and humorous",
                    "empathetic and supportive",
                    "enthusiastic and energetic",
                    "calm and patient",
                    "mentor-like and wise"
                ],
                help="Choose the personality style for the rewritten response"
            )
        
        with col2:
            transform_button = st.button("✨ Transform Response", type="primary", use_container_width=True)
        
        if transform_button:
            if not generic_response.strip():
                st.error("❌ Please provide a response to transform.")
            else:
                with st.spinner(f"Rewriting with '{persona}' persona..."):
                    try:
                        # Initialize personality engine and rewrite
                        personality_engine = PersonalityEngine(
                            user_profile=st.session_state.user_profile,
                            api_key=api_key
                        )
                        transformed_response = personality_engine.rewrite_reply(
                            original_text=generic_response,
                            persona=persona
                        )
                        
                        # Display results
                        st.subheader("🎭 Transformed Response")
                        
                        # Show before and after
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📝 Original**")
                            st.info(generic_response)
                        
                        with col2:
                            st.markdown(f"**✨ {persona.title()}**")
                            st.success(transformed_response)
                        
                    except Exception as e:
                        st.error(f"❌ Error during transformation: {str(e)}")


if __name__ == "__main__":
    main()
