import streamlit as st
from better_profanity import profanity
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Load profanity filter
profanity.load_censor_words()

# Streamlit page configuration
st.set_page_config(page_title="MIST AI - SRM Assistant", page_icon="🎓", layout="centered")

# 🎨 Custom Styles (Header Indigo + Gradient Buttons)
custom_css = """
<style>
/* Sidebar buttons */
div[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(90deg, #4F46E5, #06B6D4); /* Indigo → Cyan */
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6em 1em;
    font-weight: 500;
    transition: 0.3s;
}
div[data-testid="stSidebar"] div.stButton > button:hover {
    background: linear-gradient(90deg, #06B6D4, #4F46E5); /* Flip gradient */
    color: #84CC16 !important; /* Lime Green text */
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Sidebar with buttons
st.sidebar.title("⚙️ Controls")

# 🧑 User Profile
if "username" not in st.session_state:
    st.session_state.username = ""

st.session_state.username = st.sidebar.text_input("👤 Enter your name", st.session_state.username)

# Clear Chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.response_cache = {}
    st.sidebar.success("Chat cleared!")

# Export Chat button
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

# About button
if st.sidebar.button("ℹ️ About"):
    st.sidebar.info("MIST AI - SRM Virtual Assistant\n\nPowered by Google Gemini\nBuilt for SRM Community")

# Help button
if st.sidebar.button("❓ Help"):
    st.sidebar.warning("Type your queries in the chat box. I will answer in the SRM context.")

# SRM Header (Indigo color)
st.markdown("<h1 style='text-align:center; color:#4F46E5;'>🎓 MIST AI - SRM Virtual Assistant</h1>", unsafe_allow_html=True)
if st.session_state.username:
    st.markdown(f"<p style='text-align:center;'>👋 Hello, {st.session_state.username}! I'm your friendly SRM guide.</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align:center;'>Your friendly SRM guide for everything university-related</p>", unsafe_allow_html=True)
st.divider()

# Initialize chat history and response cache
if "messages" not in st.session_state:
    st.session_state.messages = []

if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}

# Function to get SRM-contextualized response from Gemini
def get_srm_response(query):
    """Generate SRM-contextualized response using Gemini AI"""
    try:
        prompt = f"""
        You are MIST AI, the helpful virtual assistant for SRM Institute of Science and Technology (SRMIST).

        CONTEXT: SRM is a leading private university in India with main campus in Kattankulathur, Chennai, and other campuses in Vadapalani, Ramapuram, Delhi NCR, Sonepat, and Amaravati. Known for engineering, medicine, management, law, and research programs.

        The user chatting with you is named: {st.session_state.username if st.session_state.username else "Student"}.

        Question: {query}

        Provide a helpful SRM-focused response and address the user by name if available:
        """
        
        response = model.generate_content(prompt)
        return response.text if response.text else "I couldn't generate a response. Please try again!"
        
    except Exception:
        return "I'm experiencing technical difficulties right now. Please try again in a moment!"

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
query = st.chat_input("Ask me anything about SRM or any topic...")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # Bot response logic
    if profanity.contains_profanity(query):
        bot_reply = "⚠️ Please keep our conversation respectful and appropriate."
    
    elif query.lower().strip() in ["hi", "hello", "hey", "sup", "what's up"]:
        if st.session_state.username:
            bot_reply = f"Hello {st.session_state.username}! 😊 I'm MIST AI, your SRM assistant. What would you like to know today?"
        else:
            bot_reply = "Hello! 😊 I'm MIST AI, your SRM assistant. I can help you with anything about SRM University or answer general questions in the SRM context. What would you like to know?"
    
    elif any(phrase in query.lower() for phrase in ["who are you", "what can you do", "what are you", "help me"]):
        bot_reply = "I'm MIST AI, your virtual assistant for SRM Institute of Science and Technology! 🎓\n\nI can help you with:\n• SRM admissions, courses, and departments\n• Campus facilities and student life\n• General questions answered in SRM context\n• Academic programs and opportunities\n\nJust ask me anything!"
    
    elif any(phrase in query.lower() for phrase in ["thank you", "thanks", "thx"]):
        if st.session_state.username:
            bot_reply = f"You're very welcome, {st.session_state.username}! 😊 Feel free to ask me anything else about SRM or any other topic."
        else:
            bot_reply = "You're very welcome! 😊 Feel free to ask me anything else about SRM or any other topic. I'm here to help you!"
    
    else:
        cache_key = query.lower().strip()
        if cache_key in st.session_state.response_cache:
            bot_reply = st.session_state.response_cache[cache_key]
        else:
            with st.spinner("Let me think about that in SRM context..."):
                bot_reply = get_srm_response(query)
                st.session_state.response_cache[cache_key] = bot_reply

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666; font-size:12px;'>MIST AI - Powered by Google Gemini | Built for SRM Community</p>", unsafe_allow_html=True)
