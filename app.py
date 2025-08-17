import streamlit as st
from better_profanity import profanity
import google.generativeai as genai
import os
from dotenv import load_dotenv

# -------------------- Load API Key --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# -------------------- Profanity Filter --------------------
profanity.load_censor_words()

# -------------------- Theme Config --------------------
DARK_MODE = {
    "bg": "#0a0a0a",
    "main_bg": "#1a1a1a",
    "text": "#ffffff",
    "header": "#4F46E5",
    "button": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "button_hover": "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
    "button_text": "#E0FFFF",
    "user_bubble": "#B0C4DE",
    "bot_bubble": "#2d3748",
    "bubble_text": "#B9D9EB",
    "divider": "#374151",
    "sidebar_bg": "#111827",
    "card_bg": "#1f2937"
}

LIGHT_MODE = {
    "bg": "#f9fafb",
    "main_bg": "#ffffff",
    "text": "#1f2937",
    "header": "#2563EB",
    "button": "linear-gradient(135deg, #93a5cf 0%, #e4efe9 100%)",
    "button_hover": "linear-gradient(135deg, #e4efe9 0%, #93a5cf 100%)",
    "button_text": "#111827",
    "user_bubble": "#2563EB",
    "bot_bubble": "#E5E7EB",
    "bubble_text": "#1f2937",
    "divider": "#D1D5DB",
    "sidebar_bg": "#f3f4f6",
    "card_bg": "#ffffff"
}

# -------------------- Initialize Theme --------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = DARK_MODE if st.session_state.theme == "dark" else LIGHT_MODE
dark_mode = st.session_state.theme == "dark"

# -------------------- Custom CSS --------------------
st.markdown(
    f"""
    <style>
    /* App background */
    .stApp {{
        background: linear-gradient(135deg, {theme['bg']} 0%, {theme['main_bg']} 100%);
        color: {theme['text']};
        min-height: 100vh;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {theme['sidebar_bg']} !important;
        border-right: 1px solid {theme['divider']};
        padding: 1rem !important;
    }}

    section[data-testid="stSidebar"] .stTextInput > div > div > input {{
        background-color: {theme['card_bg']} !important;
        color: {theme['text']} !important;
    }}

    /* Chat bubbles */
    .user-bubble {{
        background-color: {theme['user_bubble']};
        color: {theme['bubble_text']};
        padding: 10px 15px;
        border-radius: 15px;
        margin: 8px 0;
        text-align: right;
    }}

    .bot-bubble {{
        background-color: {theme['bot_bubble']};
        color: {theme['bubble_text']};
        padding: 10px 15px;
        border-radius: 15px;
        margin: 8px 0;
        text-align: left;
    }}

    /* Buttons */
    .stButton > button {{
        background: {theme['button']} !important;
        color: {theme['button_text']} !important;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
    }}

    .stButton > button:hover {{
        background: {theme['button_hover']} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- Example UI --------------------
st.title("🌗 Themed Chat App")

if st.button("Toggle Theme"):
    st.session_state.theme = "light" if dark_mode else "dark"
    st.rerun()

# Example chat bubbles
st.markdown(f"<div class='user-bubble'>Hey, this is the user message!</div>", unsafe_allow_html=True)
st.markdown(f"<div class='bot-bubble'>Hello, I'm the bot reply 😊</div>", unsafe_allow_html=True)
