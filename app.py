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
    "bg": "#0f172a",
    "text": "#e0f2fe",
    "header": "#4F46E5",
    "button": "linear-gradient(90deg, #4F46E5, #06B6D4)",
    "button_hover": "linear-gradient(90deg, #06B6D4, #4F46E5)",
    "button_text": "#a3e635",
    "user_bubble": "#1e40af",
    "bot_bubble": "#0891b2",
    "bubble_text": "#e0f2fe",
    "divider": "#334155"
}

LIGHT_MODE = {
    "bg": "#B0C4DE",
    "text": "#000000",
    "header": "#2563eb",
    "button": "linear-gradient(90deg, #3b82f6, #06b6d4)",
    "button_hover": "linear-gradient(90deg, #06b6d4, #3b82f6)",
    "button_text": "#111827",
    "user_bubble": "#dbeafe",
    "bot_bubble": "#e0f2fe",
    "bubble_text": "#000000",
    "divider": "#000000"
}

# -------------------- Initialize Theme --------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = DARK_MODE if st.session_state.theme == "dark" else LIGHT_MODE
dark_mode = st.session_state.theme == "dark"

# -------------------- Page Config --------------------
st.set_page_config(page_title="MIST AI - SRM Assistant", page_icon="🎓", layout="centered")

# -------------------- Sidebar --------------------
st.sidebar.title("⚙️ Controls")

# -------------------- Sun/Moon Toggle in Sidebar --------------------
if hasattr(st.sidebar, "toggle"):
    new_dark_mode = st.sidebar.toggle("🌙" if dark_mode else "☀️", value=dark_mode, key="dark_mode_toggle")
else:
    new_dark_mode = st.sidebar.checkbox("🌙" if dark_mode else "☀️", value=dark_mode, key="dark_mode_toggle")

if new_dark_mode != dark_mode:
    st.session_state.theme = "dark" if new_dark_mode else "light"
    st.rerun()

# -------------------- Custom CSS --------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {theme['bg']};
        color: {theme['text']};
    }}
    h1 {{
        color: {theme['header']} !important;
    }}
    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stSidebar"] div.stButton > button,
    div[data-testid="stSidebar"] div.stDownloadButton > button,
    div[data-testid="stChatInput"] button {{
        background: {theme['button']};
        color: #fff;
        border-radius: 10px;
        border: none;
        padding: 0.6em 1em;
        font-weight: 500;
        transition: transform 0.15s ease, background 0.3s ease, color 0.3s ease;
    }}
    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    div[data-testid="stSidebar"] div.stButton > button:hover,
    div[data-testid="stSidebar"] div.stDownloadButton > button:hover,
    div[data-testid="stChatInput"] button:hover {{
        background: {theme['button_hover']};
        color: {theme['button_text']} !important;
        transform: translateY(-1px);
    }}
    .stChatMessage.user {{
        background-color: {theme['user_bubble']} !important;
        color: {theme['bubble_text']} !important;
        border-radius: 12px;
        padding: 8px 12px;
        margin: 4px 0;
    }}
    .stChatMessage.assistant {{
        background-color: {theme['bot_bubble']} !important;
        color: {theme['bubble_text']} !important;
        border-radius: 12px;
        padding: 8px 12px;
        margin: 4px 0;
    }}
    .custom-divider {{
        border-top: 2px solid {theme['divider']};
        margin: 10px 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- User Profile --------------------
if "username" not in st.session_state:
    st.session_state.username = ""
st.session_state.username = st.sidebar.text_input("👤 Enter your name", st.session_state.username)

campus_options = ["Any campus", "Kattankulathur (KTR)", "Vadapalani", "Ramapuram", "Delhi NCR", "Sonepat", "Amaravati"]
st.session_state.campus = st.sidebar.selectbox("🏫 Campus (optional)", campus_options, index=0, key="campus_select")

focus_options = ["General", "Admissions", "Academics", "Hostel", "Fees", "Placements", "Events"]
st.session_state.focus = st.sidebar.selectbox("🎯 Focus (optional)", focus_options, index=0, key="focus_select")

# Clear Chat
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.response_cache = {}
    st.sidebar.success("Chat cleared!")

# Export Chat
if st.sidebar.button("💾 Export Chat"):
    if st.session_state.get("messages", []):
        chat_text = ""
        for msg in st.session_state.messages:
            role = "You" if msg["role"] == "user" else "MIST AI"
            chat_text += f"{role}: {msg['content']}\n\n"
        st.sidebar.download_button(
            label="⬇️ Download Chat (.txt)",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )
    else:
        st.sidebar.warning("No chat history to export!")

# About / Help
if st.sidebar.button("ℹ️ About"):
    st.sidebar.info("MIST AI - SRM Virtual Assistant\n\nPowered by Google Gemini\nBuilt for SRM Community")
if st.sidebar.button("❓ Help"):
    st.sidebar.warning("Type your queries in the chat box. I will answer in the SRM context.")

# -------------------- Header --------------------
st.markdown("<h1 style='text-align:center;'>🎓 MIST AI - SRM Virtual Assistant</h1>", unsafe_allow_html=True)
if st.session_state.username:
    st.markdown(f"<p style='text-align:center;'>👋 Hello, {st.session_state.username}! I'm your friendly SRM guide.</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align:center;'>Your friendly SRM guide for everything university-related</p>", unsafe_allow_html=True)

st.markdown(f"<div class='custom-divider'></div>", unsafe_allow_html=True)

# -------------------- Suggestions --------------------
suggestions = [
    "Admissions process and deadlines",
    "Top engineering programs at SRM",
    "Hostel facilities and fees",
    "Clubs and events this month"
]
cols = st.columns(len(suggestions))
for idx, col in enumerate(cols):
    with col:
        if st.button(suggestions[idx], key=f"suggestion_{idx}"):
            st.session_state.suggested_query = suggestions[idx]
            st.rerun()

# -------------------- Init Chat --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}

# -------------------- Response Function --------------------
def get_srm_response(query):
    try:
        prompt = f"""
        You are MIST AI, the helpful virtual assistant for SRM Institute of Science and Technology (SRMIST).

        CONTEXT: SRM is a leading private university in India with main campus in Kattankulathur, Chennai, and other campuses in Vadapalani, Ramapuram, Delhi NCR, Sonepat, and Amaravati. Known for engineering, medicine, management, law, and research programs.

        The user chatting with you is named: {st.session_state.username if st.session_state.username else "Student"}.
        Preferred campus: {st.session_state.get('campus', 'Any campus')}.
        Preferred focus: {st.session_state.get('focus', 'General')}.

        Question: {query}

        Provide a helpful SRM-focused response. If a campus or focus is given, tailor the answer accordingly and address the user by name if available. Keep it concise with bullets when useful:
        """
        response = model.generate_content(prompt)
        return response.text if response.text else "I couldn't generate a response. Please try again!"
    except Exception:
        return "I'm experiencing technical difficulties right now. Please try again in a moment!"

# -------------------- Chat Display --------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🎓"):
        st.write(msg["content"])

# -------------------- Chat Input --------------------
query = st.session_state.pop("suggested_query", None)
if query is None:
    query = st.chat_input("Ask me anything about SRM or any topic...", key="chat_input")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.write(query)

    # Bot Logic
    if profanity.contains_profanity(query):
        bot_reply = "⚠️ Please keep our conversation respectful and appropriate."
    elif query.lower().strip() in ["hi", "hello", "hey", "sup", "what's up"]:
        bot_reply = f"Hello {st.session_state.username}! 😊 I'm MIST AI, your SRM assistant." if st.session_state.username else "Hello! 😊 I'm MIST AI, your SRM assistant."
    elif any(phrase in query.lower() for phrase in ["who are you", "what can you do", "what are you", "help me"]):
        bot_reply = "I'm MIST AI 🎓\n\nI can help you with:\n• Admissions, courses, and departments\n• Campus facilities & student life\n• General questions in SRM context\n• Academic programs & opportunities"
    elif any(phrase in query.lower() for phrase in ["thank you", "thanks", "thx"]):
        bot_reply = f"You're very welcome, {st.session_state.username}! 😊" if st.session_state.username else "You're very welcome! 😊"
    else:
        cache_key = query.lower().strip()
        if cache_key in st.session_state.response_cache:
            bot_reply = st.session_state.response_cache[cache_key]
        else:
            with st.spinner("Let me think about that in SRM context..."):
                bot_reply = get_srm_response(query)
                st.session_state.response_cache[cache_key] = bot_reply

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant", avatar="🎓"):
        st.write(bot_reply)

# -------------------- Footer --------------------
st.markdown(f"<div class='custom-divider'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:12px;'>MIST AI - Powered by Google Gemini | Built for SRM Community</p>", unsafe_allow_html=True)
