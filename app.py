"""
AI Memory & Personality Engine - Streamlit Application

A prototype that extracts structured memory from chat history
and demonstrates personality-based response rewriting.
"""

import streamlit as st

import config
from memory_engine import MemoryEngine
from personality_engine import PersonalityEngine


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


DEFAULT_RESPONSE = (
    "I can help you learn programming. Let's start with the basics and work "
    "through some examples together. Practice is key to success."
)

PERSONAS = [
    "friendly and encouraging",
    "professional and formal",
    "casual and humorous",
    "empathetic and supportive",
    "enthusiastic and energetic",
    "calm and patient",
    "mentor-like and wise",
]

# (title, icon, UserProfile field, badge color)
PROFILE_SECTIONS = [
    ("Facts", ":material/badge:", "facts", "blue"),
    ("Preferences", ":material/favorite:", "preferences", "violet"),
    ("Emotional patterns", ":material/mood:", "emotional_patterns", "orange"),
]


def parse_chat(chat_log: str) -> list[tuple[str, str]]:
    """Split a 'User: ... / AI: ...' transcript into (role, text) turns for the preview."""
    turns = []
    for line in chat_log.splitlines():
        speaker, sep, text = line.partition(":")
        role = speaker.strip().lower()
        if sep and role in ("user", "ai", "assistant"):
            turns.append(("user" if role == "user" else "assistant", text.strip()))
        elif line.strip() and turns:
            # A line without a speaker continues the previous turn
            turns[-1] = (turns[-1][0], turns[-1][1] + "\n" + line.strip())
    return turns


def render_sidebar() -> str:
    """API key input and app info. Returns the key, or "" if none was entered."""
    with st.sidebar:
        st.subheader(":material/key: Your API key")
        key_input = st.text_input(
            "Google Gemini API key",
            type="password",
            placeholder="Paste your Gemini API key",
            help="Used only for this browser session and never stored.",
        )
        # Bring-your-own-key: the app never falls back to a server-side key, so a public
        # deploy can't spend the owner's quota. The key lives only in this session.
        api_key = key_input.strip() if key_input else ""

        if api_key:
            st.success("Key set for this session", icon=":material/check_circle:")
        else:
            st.caption("[Get a free key from Google AI Studio](https://aistudio.google.com/apikey)")

        st.divider()
        st.subheader(":material/info: How it works")
        st.markdown(
            "1. Paste a conversation\n"
            "2. Gemini extracts a structured profile\n"
            "3. Pick a persona to rewrite a reply using that profile"
        )
        st.caption(":material/lock: Your key is never stored or logged.")
        st.badge(config.GEMINI_MODEL, icon=":material/memory:", color="gray")
    return api_key


def render_conversation(api_key: str) -> None:
    """Step 1: chat input with a chat-bubble preview, plus the extract button."""
    with st.container(border=True):
        st.subheader(":material/forum: 1. Conversation")
        edit_tab, preview_tab = st.tabs(["Edit", "Preview"])
        with edit_tab:
            chat_history = st.text_area(
                "Chat history",
                value=DEFAULT_CHAT,
                height=300,
                label_visibility="collapsed",
                help="Use 'User:' and 'AI:' at the start of each turn.",
            )
        with preview_tab, st.container(height=300, border=False):
            turns = parse_chat(chat_history)
            if not turns:
                st.caption("Start lines with 'User:' or 'AI:' to see the chat preview.")
            for role, text in turns:
                avatar = ":material/person:" if role == "user" else ":material/smart_toy:"
                with st.chat_message(role, avatar=avatar):
                    st.markdown(text)

        if st.button(
            "Extract profile",
            type="primary",
            icon=":material/psychology:",
            disabled=not api_key,
        ):
            if not chat_history.strip():
                st.error("Please paste a conversation first.", icon=":material/error:")
                return
            with st.status("Analyzing the conversation...") as status:
                try:
                    status.write(f"Sending the chat to {config.GEMINI_MODEL}")
                    profile = MemoryEngine(api_key=api_key).extract_from_chat(chat_history)
                except Exception as e:
                    status.update(label="Extraction failed", state="error", expanded=True)
                    st.error(str(e), icon=":material/error:")
                    return
                status.update(label="Profile extracted", state="complete")
            st.session_state.user_profile = profile
            st.session_state.rewrite = None  # an old rewrite used the old profile
            st.toast("Profile ready", icon=":material/check_circle:")


def render_profile() -> None:
    """Step 2: the extracted profile as three cards."""
    with st.container(border=True):
        st.subheader(":material/person: 2. Extracted profile")
        profile = st.session_state.user_profile
        if not profile:
            st.caption("Run **Extract profile** to see what the model learns about the user.")
            return

        for column, (title, icon, field, color) in zip(st.columns(3), PROFILE_SECTIONS):
            items = getattr(profile, field)
            with column, st.container(border=True, height="stretch"):
                st.markdown(f"**{icon} {title}** :{color}-badge[{len(items)}]")
                if items:
                    st.markdown("\n".join(f"- {item}" for item in items))
                else:
                    st.caption("Nothing found")

        with st.expander("Raw JSON", icon=":material/data_object:"):
            st.json(profile.model_dump())


def render_rewrite(api_key: str) -> None:
    """Step 3: rewrite a generic reply in a chosen persona, shown before vs after."""
    with st.container(border=True):
        st.subheader(":material/theater_comedy: 3. Personalized rewrite")
        profile = st.session_state.user_profile

        generic_response = st.text_area("Generic AI response", value=DEFAULT_RESPONSE, height=100)
        persona = st.pills(
            "Persona",
            PERSONAS,
            default=PERSONAS[0],
            format_func=str.capitalize,
            required=True,  # one persona is always selected
        )

        if st.button(
            "Rewrite response",
            type="primary",
            icon=":material/auto_awesome:",
            disabled=not (api_key and profile),
            help=None if profile else "Extract a profile first",
        ):
            if not generic_response.strip():
                st.error("Please enter a response to rewrite.", icon=":material/error:")
            else:
                with st.spinner(f"Rewriting as {persona}..."):
                    try:
                        engine = PersonalityEngine(user_profile=profile, api_key=api_key)
                        rewritten = engine.rewrite_reply(original_text=generic_response, persona=persona)
                        # Keep the result in session state so it survives reruns
                        st.session_state.rewrite = {
                            "persona": persona,
                            "original": generic_response,
                            "text": rewritten,
                        }
                    except Exception as e:
                        st.error(str(e), icon=":material/error:")

        result = st.session_state.rewrite
        if result:
            before, after = st.columns(2)
            with before, st.container(border=True, height="stretch"):
                st.markdown(":gray-badge[Before] **Generic reply**")
                st.markdown(result["original"])
            with after, st.container(border=True, height="stretch"):
                st.markdown(f":violet-badge[After] **{result['persona'].capitalize()}**")
                st.markdown(result["text"])


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="AI Memory & Personality Engine",
        page_icon=":material/psychology:",
        layout="wide",
    )
    st.session_state.setdefault("user_profile", None)
    st.session_state.setdefault("rewrite", None)

    api_key = render_sidebar()

    st.title("AI Memory & Personality Engine")
    st.markdown(
        "Turn a raw conversation into a structured user profile, then rewrite "
        "replies so they feel personal.  \n"
        ":violet-badge[:material/forum: Paste a chat] "
        ":violet-badge[:material/psychology: Extract a profile] "
        ":violet-badge[:material/auto_awesome: Personalize replies]"
    )
    if not api_key:
        st.info(
            "Add your Google Gemini API key in the sidebar to run the demo. "
            "[Get one free](https://aistudio.google.com/apikey).",
            icon=":material/key:",
        )

    render_conversation(api_key)
    render_profile()
    render_rewrite(api_key)

    st.caption(
        "Built with Streamlit, LangChain and Google Gemini · "
        "[Source on GitHub](https://github.com/VedPawar1410/memory-extraction)"
    )


if __name__ == "__main__":
    main()
