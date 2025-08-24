import streamlit as st
from better_profanity import profanity
import google.generativeai as genai
import os
from dotenv import load_dotenv
from database import get_answer_from_db, add_qa_pair
def get_srm_response(query):
    db_answer = get_answer_from_db(query)
    if db_answer:
        print(f"✅ Answer from DB for '{query}': {db_answer}")  # Debug log
        return db_answer

    try:
        prompt = f"""
        You are MIST AI, the helpful virtual assistant for SRM Institute of Science and Technology.

        Question: {query}

        Provide a helpful and concise response.
        """
        response = model.generate_content(prompt)
        answer = response.text if response.text else "I couldn't generate a response. Please try again!"

        add_qa_pair(query, answer)
        print(f"💾 Saved new Gemini answer to DB for '{query}': {answer}")  # Debug log

        return answer
    except Exception as e:
        print("❌ Error while generating response:", e)  # Debug log
        return "I'm experiencing technical difficulties right now. Please try again later."

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


profanity.load_censor_words()


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
    "bg": "#B9D9EB",
    "main_bg": "#F0F8FF",
    "text": "#1e293b",
    "header": "#3b82f6",
    "button": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "button_hover": "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
    "button_text": "#002244",
    "user_bubble": "#132257",
    "bot_bubble": "#132257",
    "bubble_text": "#13274F",
    "divider": "#cbd5e1",
    "sidebar_bg": "#5D8AA8",
    "card_bg": "#1E2952"
}


if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = DARK_MODE if st.session_state.theme == "dark" else LIGHT_MODE
dark_mode = st.session_state.theme == "dark"

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="MIST AI - SRM Assistant", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    f"""
    <style>
    /* Global Styles */
    .stApp {{
        background: linear-gradient(135deg, {theme['bg']} 0%, {theme['main_bg']} 100%);
        color: {theme['text']};
        min-height: 100vh;
    }}
    
    /* Enhanced Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {theme['sidebar_bg']} !important;
        border-right: 1px solid {theme['divider']};
        padding: 1rem !important;
    }}
    
    /* Sidebar content styling */
    section[data-testid="stSidebar"] .stMarkdown {{
        background-color: transparent !important;
    }}
    
    section[data-testid="stSidebar"] .stTextInput > div > div > input {{
        background-color: {theme['card_bg']} !important;
        color: {theme['text']} !important;
        border: 2px solid {theme['divider']} !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-size: 14px !important;
    }}
    
    section[data-testid="stSidebar"] .stSelectbox > div > div > select {{
        background-color: {theme['card_bg']} !important;
        color: {theme['text']} !important;
        border: 2px solid {theme['divider']} !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-size: 14px !important;
    }}
    
    section[data-testid="stSidebar"] .stButton > button {{
        background: {theme['button']} !important;
        color: {theme['button_text']} !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        margin: 5px 0 !important;
    }}
    
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: {theme['button_hover']} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }}
    
    section[data-testid="stSidebar"] .stExpander {{
        background-color: transparent !important;
        border: 1px solid {theme['divider']} !important;
        border-radius: 10px !important;
    }}
    
    section[data-testid="stSidebar"] .stExpander > div > div {{
        background-color: {theme['card_bg']} !important;
        border-radius: 10px !important;
    }}
    
    section[data-testid="stSidebar"] .stExpander > div > div > div {{
        background-color: {theme['card_bg']} !important;
        border-radius: 10px !important;
    }}
    
    section[data-testid="stSidebar"] .stCheckbox {{
        background-color: transparent !important;
    }}
    
    section[data-testid="stSidebar"] .stSelectSlider {{
        background-color: transparent !important;
    }}
    
    section[data-testid="stSidebar"] .stSelectSlider > div > div > div {{
        background-color: {theme['card_bg']} !important;
        border-radius: 10px !important;
    }}
    
    /* Enhanced Theme Toggle Styling */
    section[data-testid="stSidebar"] .stToggle > div > div {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 2px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }}
    
    section[data-testid="stSidebar"] .stToggle > div > div > div {{
        background: white !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
    }}
    
    section[data-testid="stSidebar"] .stToggle > div > div > div:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }}
    
    /* Enhanced Checkbox Styling for theme toggle */
    section[data-testid="stSidebar"] .stCheckbox > div > div > div {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }}
    
    section[data-testid="stSidebar"] .stCheckbox > div > div > div:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }}
    
    section[data-testid="stSidebar"] .stCheckbox > div > div > div:checked {{
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4) !important;
    }}
    
    /* Header Styling */
    h1 {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    /* Button Styling */
    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stChatInput"] button {{
        background: {theme['button']} !important;
        color: {theme['button_text']} !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        width: 100% !important;
        margin: 5px 0 !important;
    }}
    
    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    div[data-testid="stChatInput"] button:hover {{
        background: {theme['button_hover']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
    }}
    
    /* Chat Message Styling */
    .stChatMessage {{
        background-color: transparent !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 15px 0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        border: 1px solid {theme['divider']} !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        cursor: pointer !important;
    }}
    
    .stChatMessage:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
    }}
    
    .stChatMessage.user {{
        background: linear-gradient(135deg, {theme['user_bubble']} 0%, #A8C0E0 50%, #B8CCE8 100%) !important;
        color: {theme['bubble_text']} !important;
        margin-left: 20% !important;
        margin-right: 5% !important;
        border: 2px solid rgba(176, 196, 222, 0.4) !important;
        box-shadow: 0 8px 25px rgba(176, 196, 222, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }}
    
    .stChatMessage.user:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(176, 196, 222, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(176, 196, 222, 0.6) !important;
    }}
    
    .stChatMessage.user::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent) !important;
        transition: left 0.6s ease !important;
    }}
    
    .stChatMessage.user:hover::before {{
        left: 100% !important;
    }}
    
    /* User avatar enhancement */
    .stChatMessage.user .stChatMessageContent {{
        position: relative !important;
        z-index: 2 !important;
    }}
    
    .stChatMessage.assistant {{
        background: linear-gradient(135deg, {theme['bot_bubble']} 0%, #3a4a5a 50%, #2d3748 100%) !important;
        color: {theme['bubble_text']} !important;
        margin-right: 20% !important;
        margin-left: 5% !important;
        border: 2px solid rgba(45, 55, 72, 0.4) !important;
        box-shadow: 0 8px 25px rgba(45, 55, 72, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }}
    
    .stChatMessage.assistant:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(45, 55, 72, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(45, 55, 72, 0.6) !important;
    }}
    
    .stChatMessage.assistant::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        right: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent) !important;
        transition: right 0.6s ease !important;
    }}
    
    .stChatMessage.assistant:hover::before {{
        right: 100% !important;
    }}
    
    /* AI avatar enhancement */
    .stChatMessage.assistant .stChatMessageContent {{
        position: relative !important;
        z-index: 2 !important;
    }}
    
    /* Enhanced Profile Images and Interactive Elements */
    .stChatMessage [data-testid="stChatMessageAvatar"] {{
        transition: all 0.3s ease !important;
        border-radius: 50% !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        border: 3px solid transparent !important;
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        padding: 2px !important;
    }}
    
    .stChatMessage [data-testid="stChatMessageAvatar"]:hover {{
        transform: scale(1.1) rotate(5deg) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }}
    
    .stChatMessage.user [data-testid="stChatMessageAvatar"] {{
        background: linear-gradient(45deg, #B0C4DE, #A8C0E0) !important;
        border-color: rgba(176, 196, 222, 0.6) !important;
    }}
    
    .stChatMessage.assistant [data-testid="stChatMessageAvatar"] {{
        background: linear-gradient(45deg, #4F46E5, #667eea) !important;
        border-color: rgba(79, 70, 229, 0.6) !important;
    }}
    
    /* Chat message content enhancement */
    .stChatMessage [data-testid="stChatMessageContent"] {{
        transition: all 0.3s ease !important;
        border-radius: 18px !important;
        padding: 12px 18px !important;
    }}
    
    .stChatMessage:hover [data-testid="stChatMessageContent"] {{
        transform: scale(1.01) !important;
    }}
    
    /* Interactive chat area */
    .stChatMessage {{
        position: relative !important;
    }}
    
    .stChatMessage::after {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        border-radius: 20px !important;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent) !important;
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
        pointer-events: none !important;
    }}
    
    .stChatMessage:hover::after {{
        opacity: 1 !important;
    }}
    
    /* Ensure chat messages have relative positioning for copy button */
    .stChatMessage {{
        position: relative !important;
    }}
    
    /* Copy Button Styling */
    .copy-button {{
        position: absolute !important;
        top: 8px !important;
        right: 8px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        color: #333 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 28px !important;
        height: 28px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        opacity: 0 !important;
        transition: all 0.3s ease !important;
        font-size: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        z-index: 10 !important;
    }}
    
    .stChatMessage:hover .copy-button {{
        opacity: 1 !important;
        transform: scale(1.1) !important;
    }}
    
    .copy-button:hover {{
        background: rgba(255, 255, 255, 1) !important;
        transform: scale(1.2) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }}
    
    .copy-button.copied {{
        background: #10B981 !important;
        color: white !important;
    }}
    
    /* Chat Section Enhancement */
    .chat-section {{
        position: relative !important;
        min-height: 200px !important;
        transition: all 0.3s ease !important;
    }}
    
    .chat-section:hover {{
        transform: translateY(-1px) !important;
    }}
    
    /* Enhanced suggestion buttons */
    .suggestion-section {{
        margin: 20px 0 !important;
        padding: 15px !important;
        background: linear-gradient(135deg, rgba(176, 196, 222, 0.1) 0%, rgba(168, 192, 224, 0.05) 100%) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(176, 196, 222, 0.2) !important;
    }}
    
    .suggestion-section .stButton > button {{
        transition: all 0.3s ease !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }}
    
    .suggestion-section .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(176, 196, 222, 0.3) !important;
    }}
    
    /* Input Styling */
    div[data-testid="stChatInput"] {{
        background-color: white !important;
        border-radius: 20px !important;
        padding: 10px !important;
        border: 2px solid {theme['divider']} !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }}
    
    div[data-testid="stChatInput"] textarea {{
        background-color: white !important;
        color: black !important;
        border: none !important;
        font-size: 16px !important;
        outline: none !important;
    }}
    
    /* Chat input container styling */
    div[data-testid="stChatInput"] > div {{
        background-color: white !important;
        border-radius: 20px !important;
    }}
    
    /* Chat input form styling */
    div[data-testid="stChatInput"] form {{
        background-color: white !important;
        border-radius: 20px !important;
    }}
    
    /* Chat input row styling */
    div[data-testid="stChatInput"] .stChatInputRow {{
        background-color: white !important;
        border-radius: 20px !important;
        align-items: center !important;
        display: flex !important;
        gap: 10px !important;
    }}
    
    /* Send Button Styling */
    div[data-testid="stChatInput"] button {{
        background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        margin: 0 !important;
        min-width: 60px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        flex-shrink: 0 !important;
    }}
    
    div[data-testid="stChatInput"] button:hover {{
        background: linear-gradient(135deg, #06B6D4 0%, #4F46E5 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
    }}
    
    /* Sidebar Input Styling */
    .stTextInput > div > div > input {{
        background-color: {theme['card_bg']} !important;
        color: {theme['text']} !important;
        border: 2px solid {theme['divider']} !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }}
    
    .stSelectbox > div > div > select {{
        background-color: {theme['card_bg']} !important;
        color: {theme['text']} !important;
        border: 2px solid {theme['divider']} !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }}
    
    /* Divider Styling */
    .custom-divider {{
        background: linear-gradient(90deg, transparent, {theme['divider']}, transparent);
        height: 2px;
        margin: 20px 0;
        border-radius: 1px;
    }}
    
    /* Welcome Message - Larger and more prominent */
    .welcome-message {{
        background: linear-gradient(135deg, {theme['card_bg']} 0%, {theme['bg']} 100%);
        border: 1px solid {theme['divider']};
        border-radius: 25px;
        padding: 30px;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        max-width: 100% !important;
    }}
    
    /* Main content area - Use more space */
    .main .block-container {{
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 1rem !important;
    }}
    
    /* When sidebar is collapsed, use even more space */
    section[data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container {{
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }}
    
    /* Header - Make it larger and more prominent */
    h1 {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 4rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin: 1rem 0 1.5rem 0 !important;
        text-shadow: 0 6px 12px rgba(0,0,0,0.2);
        letter-spacing: -0.02em !important;
    }}
    
    /* Suggestions section - Better spacing and layout */
    .suggestion-section {{
        margin: 1.5rem 0 !important;
        padding: 0 !important;
    }}
    
    /* Suggestion cards - Larger and more prominent */
    .suggestion-card {{
        background: linear-gradient(135deg, {theme['card_bg']} 0%, {theme['bg']} 100%);
        border: 1px solid {theme['divider']};
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .suggestion-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }}
    
    /* Chat section - Use more space */
    .chat-section {{
        margin: 0.5rem 0 !important;
        padding: 0 !important;
    }}
    
    /* Chat messages - Better spacing */
    .stChatMessage {{
        margin: 15px 0 !important;
        max-width: 90% !important;
    }}
    
    .stChatMessage.user {{
        margin-left: 10% !important;
        margin-right: 5% !important;
    }}
    
    .stChatMessage.assistant {{
        margin-right: 10% !important;
        margin-left: 5% !important;
    }}
    
    /* Footer */
    .footer {{
        background: linear-gradient(135deg, {theme['card_bg']} 0%, {theme['bg']} 100%);
        border-top: 1px solid {theme['divider']};
        padding: 20px;
        text-align: center;
        margin-top: 40px;
        border-radius: 20px 20px 0 0;
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        h1 {{
            font-size: 2rem !important;
        }}
        .stChatMessage.user,
        .stChatMessage.assistant {{
            margin-left: 5% !important;
            margin-right: 5% !important;
        }}
    }}
    
    /* Improve suggestion buttons layout */
    .stButton > button {{
        min-height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Ensure sidebar toggle button is visible */
    button[aria-label="Toggle sidebar"] {{
        background: {theme['button']} !important;
        color: {theme['button_text']} !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 2000 !important;
    }}
    
    button[aria-label="Toggle sidebar"]:hover {{
        background: {theme['button_hover']} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.3) !important;
    }}
    
    /* Enhanced Light Theme Styling */
    .stApp[data-theme="light"] {{
        background: linear-gradient(135deg, #B9D9EB 0%, #F0F8FF 25%, #B9D9EB 50%, #F0F8FF 75%, #B9D9EB 100%) !important;
    }}
    
    .stApp[data-theme="light"] .stChatMessage.user {{
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #2563EB 100%) !important;
        color: white !important;
        border: 2px solid rgba(30, 58, 138, 0.4) !important;
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.3) !important;
    }}
    
    .stApp[data-theme="light"] .stChatMessage.assistant {{
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important;
        color: white !important;
        border: 2px solid rgba(15, 23, 42, 0.4) !important;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.3) !important;
    }}
    
    /* Light theme textbox styling */
    .stApp[data-theme="light"] .stTextInput > div > div > input {{
        color: white !important;
        background-color: black !important;
    }}
    
    .stApp[data-theme="light"] .stSelectbox > div > div > select {{
        color: white !important;
    }}
    
    /* Ensure chat input is always white */
    .stApp[data-theme="light"] div[data-testid="stChatInput"] {{
        background-color: white !important;
    }}
    
    .stApp[data-theme="light"] div[data-testid="stChatInput"] textarea {{
        background-color: white !important;
        color: black !important;
    }}
    
    .stApp[data-theme="light"] div[data-testid="stChatInput"] > div {{
        background-color: white !important;
    }}
    
    .stApp[data-theme="light"] div[data-testid="stChatInput"] form {{
        background-color: white !important;
    }}
    
    .stApp[data-theme="light"] div[data-testid="stChatInput"] .stChatInputRow {{
        background-color: white !important;
    }}
    
    /* Light theme headings - Quick Suggestions and Chat */
    .stApp[data-theme="light"] h3 {{
        color: black !important;
    }}
    
    /* Light theme chat bubbles - both user and assistant */
    .stApp[data-theme="light"] .stChatMessage.user {{
        background: linear-gradient(135deg, #E5E7EB 0%, #F3F4F6 50%, #FFFFFF 100%) !important;
        color: #1F2937 !important;
        border: 2px solid rgba(209, 213, 219, 0.4) !important;
        box-shadow: 0 6px 20px rgba(156, 163, 175, 0.3) !important;
    }}
    
    .stApp[data-theme="light"] .stChatMessage.assistant {{
        background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 50%, #E5E7EB 100%) !important;
        color: #1F2937 !important;
        border: 2px solid rgba(209, 213, 219, 0.4) !important;
        box-shadow: 0 6px 20px rgba(156, 163, 175, 0.3) !important;
    }}
    
    /* Chat bubble text styling - specific to chat messages only */
    .stApp[data-theme="light"] .stChatMessage .stChatMessageContent {{
        color: #1F2937 !important;
        font-weight: 500 !important;
        text-shadow: none !important;
    }}
    
    .stApp[data-theme="light"] .stChatMessage.user .stChatMessageContent {{
        color: #1F2937 !important;
        font-weight: 600 !important;
        text-shadow: none !important;
    }}
    
    .stApp[data-theme="light"] .stChatMessage.assistant .stChatMessageContent {{
        color: #1F2937 !important;
        font-weight: 500 !important;
        text-shadow: none !important;
    }}
    
    /* Ensure chat message text is always dark gray and readable */
    .stApp[data-theme="light"] .stChatMessage p {{
        color: #1F2937 !important;
        font-weight: 500 !important;
    }}
    
    .stApp[data-theme="light"] .stChatMessage div {{
        color: #1F2937 !important;
    }}
    
    /* AGGRESSIVE OVERRIDE - Force all chat text to be dark in light theme */
    .stApp[data-theme="light"] .stChatMessage,
    .stApp[data-theme="light"] .stChatMessage *,
    .stApp[data-theme="light"] .stChatMessageContent,
    .stApp[data-theme="light"] .stChatMessageContent *,
    .stApp[data-theme="light"] [data-testid="stChatMessageContent"],
    .stApp[data-theme="light"] [data-testid="stChatMessageContent"] * {{
        color: #1F2937 !important;
        color: #000000 !important;
    }}
    
    /* Force specific text elements */
    .stApp[data-theme="light"] .stChatMessage p,
    .stApp[data-theme="light"] .stChatMessage span,
    .stApp[data-theme="light"] .stChatMessage div,
    .stApp[data-theme="light"] .stChatMessage strong,
    .stApp[data-theme="light"] .stChatMessage em {{
        color: #000000 !important;
        color: #1F2937 !important;
    }}
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Add JavaScript for copy functionality
st.components.v1.html(
    """
    <script>
    function addCopyButtons() {
        const chatMessages = document.querySelectorAll('.stChatMessage');
        chatMessages.forEach((message, index) => {
            if (!message.querySelector('.copy-button')) {
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.innerHTML = '📋';
                copyButton.title = 'Copy message';
                copyButton.style.cssText = 'position: absolute; top: 8px; right: 8px; background: rgba(255, 255, 255, 0.9); color: #333; border: none; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; cursor: pointer; opacity: 0; transition: all 0.3s ease; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10;';
                
                copyButton.addEventListener('click', function() {
                    const messageContent = message.querySelector('[data-testid="stChatMessageContent"]');
                    if (messageContent) {
                        const text = messageContent.textContent || messageContent.innerText;
                        navigator.clipboard.writeText(text).then(() => {
                            copyButton.innerHTML = '✓';
                            copyButton.style.background = '#10B981';
                            copyButton.style.color = 'white';
                            setTimeout(() => {
                                copyButton.innerHTML = '📋';
                                copyButton.style.background = 'rgba(255, 255, 255, 0.9)';
                                copyButton.style.color = '#333';
                            }, 2000);
                        });
                    }
                });
                
                message.appendChild(copyButton);
                
                // Show button on hover
                message.addEventListener('mouseenter', () => {
                    copyButton.style.opacity = '1';
                    copyButton.style.transform = 'scale(1.1)';
                });
                
                message.addEventListener('mouseleave', () => {
                    copyButton.style.opacity = '0';
                    copyButton.style.transform = 'scale(1)';
                });
            }
        });
    }
    
    // Run when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addCopyButtons);
    } else {
        addCopyButtons();
    }
    
    // Run after Streamlit updates
    const observer = new MutationObserver(addCopyButtons);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
)

# -------------------- Sidebar --------------------
with st.sidebar:
    # Header with Logo and Title
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">🎓 MIST AI</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">SRM Virtual Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Beautiful Theme Toggle
    st.markdown("### 🌓 Theme")
    
    # Create a custom theme switcher with better styling
    if hasattr(st, "toggle"):
        new_dark_mode = st.toggle(
            "🌙 Dark Mode" if dark_mode else "☀️ Light Mode", 
            value=dark_mode, 
            key="dark_mode_toggle",
            help="Switch between dark and light themes"
        )
    else:
        new_dark_mode = st.checkbox(
            "🌙 Dark Mode" if dark_mode else "☀️ Light Mode", 
            value=dark_mode, 
            key="dark_mode_toggle",
            help="Switch between dark and light themes"
        )
    

    
    if new_dark_mode != dark_mode:
        st.session_state.theme = "dark" if new_dark_mode else "light"
        st.rerun()
    
    st.markdown("---")
    
    # User Profile Section
    st.markdown("### 👤 Profile")
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    st.session_state.username = st.text_input("Your Name", st.session_state.username, placeholder="Enter your name")

    campus_options = ["Any campus", "Kattankulathur (KTR)", "Vadapalani", "Ramapuram", "Delhi NCR", "Sonepat", "Amaravati"]
    st.session_state.campus = st.selectbox("Campus", campus_options, index=0, key="campus_select")
    
    focus_options = ["General", "Admissions", "Academics", "Hostela", "Fees", "Placements", "Events"]
    st.session_state.focus = st.selectbox("Focus Area", focus_options, index=0, key="focus_select")
    
    st.markdown("---")
    
    # Quick Actions Section
    st.markdown("### ⚡ Quick Actions")
    
    # Action Buttons in Grid
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", help="Clear chat history", use_container_width=True):
            st.session_state.messages = []
            st.session_state.response_cache = {}
            st.success("Chat cleared!")

    with col2:
        if st.button("💾 Export", help="Export chat to file", use_container_width=True):
            if st.session_state.get("messages", []):
                chat_text = ""
                for msg in st.session_state.messages:
                    role = "You" if msg["role"] == "user" else "MIST AI"
                    chat_text += f"{role}: {msg['content']}\n\n"
                st.download_button(
                    label="⬇️ Download",
                    data=chat_text,
                    file_name="chat_history.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("No chat history!")
    
    # Additional Actions
    if st.button("📊 Statistics", help="View chat statistics", use_container_width=True):
        if st.session_state.get("messages", []):
            total_messages = len(st.session_state.messages)
            user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
            bot_messages = len([msg for msg in st.session_state.messages if msg["role"] == "assistant"])
            
            st.info(f"""
            **📈 Chat Statistics:**
            - **Total:** {total_messages}
            - **You:** {user_messages}
            - **AI:** {bot_messages}
            """)
        else:
            st.warning("No chat history to analyze!")
    
    if st.button("🔄 Reset", help="Reset all settings", use_container_width=True):
        if st.button("⚠️ Confirm", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Chat Settings Section
    st.markdown("### ⚙️ Chat Settings")
    with st.expander("Response Configuration", expanded=False):
        response_length = st.select_slider(
            "Response Length",
            options=["Short", "Medium", "Long"],
            value="Medium"
        )
        
        st.markdown("**Features:**")
        st.markdown("🎤 **Voice Input** - Coming Soon")
        st.markdown("🖼️ **Image Support** - Coming Soon")
    
    st.markdown("---")
    
    # Help Section - Split into two organized sections
    st.markdown("### ℹ️ Help & Info")
    
    # Section 1: About MIST AI
    with st.expander("🤖 About MIST AI", expanded=False):
        st.success("**MIST AI - SRM Virtual Assistant**\n\nPowered by Google Gemini\nBuilt for SRM Community")
        
        st.markdown("**💡 Quick Tips:**")
        st.markdown("• Ask about admissions, courses, or campus life")
        st.markdown("• Specify your campus for personalized answers")
        st.markdown("• Use the focus option for relevant information")
        st.markdown("• I can help with general questions too!")
        
        st.markdown("**🔧 How to Use:**")
        st.markdown("• Type your questions in the chat box")
        st.markdown("• Use suggestion buttons for quick queries")
        st.markdown("• Set your campus and focus for better answers")
    
    # Section 2: About SRM
    with st.expander("🏫 About SRM", expanded=False):
        st.info("**SRM Institute of Science and Technology (SRMIST)**")
        
        st.markdown("**🎓 University Overview:**")
        st.markdown("• Leading private university in India")
        st.markdown("• Multiple campuses across India")
        st.markdown("• Known for engineering, medicine, management, law, and research")
        st.markdown("• Strong industry connections and placements")
        
        st.markdown("**🏛️ Campus Locations:**")
        st.markdown("• **Main Campus:** Kattankulathur (KTR), Chennai")
        st.markdown("• **Other Campuses:** Vadapalani, Ramapuram, Delhi NCR, Sonepat, Amaravati")
        
        st.markdown("**🔗 Official Links:**")
        st.markdown("• [SRM Official Website](https://www.srmist.edu.in)")
        st.markdown("• [Admissions Portal](https://admissions.srmist.edu.in)")
        st.markdown("• [Student Portal](https://student.srmist.edu.in)")
        st.markdown("• [Research & Innovation](https://www.srmist.edu.in/research)")
        st.markdown("• [International Relations](https://www.srmist.edu.in/international)")
    
    st.markdown("---")
    
    # Footer with Version
    st.markdown(f"""
    <div style="text-align: center; padding: 15px 0; background: {'#002147' if st.session_state.theme == 'light' else 'rgba(102, 126, 234, 0.1)'}; border-radius: 10px;">
        <p style="font-size: 12px; color: {'white' if st.session_state.theme == 'light' else '#667eea'}; margin: 0; font-weight: 600;">MIST AI v1.0</p>
        <p style="font-size: 10px; color: {'rgba(255,255,255,0.8)' if st.session_state.theme == 'light' else '#6b7280'}; margin: 5px 0 0 0;">Powered by Gemini</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Main Content --------------------
# Header
st.markdown("<h1>🎓 MIST AI - SRM Virtual Assistant</h1>", unsafe_allow_html=True)

# Welcome Message
if st.session_state.username:
    st.markdown(f"<p style='text-align:center;'>👋 Hello, {st.session_state.username}! I'm your friendly SRM guide.</p>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="welcome-message">
        <h3>👋 Welcome to MIST AI!</h3>
        <p>Your friendly SRM guide for everything university-related</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# -------------------- Suggestions --------------------
st.markdown("### 💡 Quick Suggestions")
st.markdown('<div class="suggestion-section">', unsafe_allow_html=True)
suggestions = [
    "Admissions process and deadlines",
    "Top engineering programs at SRM",
    "Hostel facilities and fees",
    "Clubs and events this month"
]

cols = st.columns(len(suggestions))
for idx, col in enumerate(cols):
    with col:
        if st.button(suggestions[idx], key=f"suggestion_{idx}", use_container_width=True):
            st.session_state.suggested_query = suggestions[idx]
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# -------------------- Init Chat --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}



# -------------------- Chat Display --------------------
st.markdown("### 💬 Chat")
st.markdown('<div class="chat-section">', unsafe_allow_html=True)

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🎓"):
        st.write(msg["content"])

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Chat Input --------------------
# Handle suggested queries first
suggested_query = st.session_state.get("suggested_query", None)
if suggested_query:
    # Process the suggested query immediately
    query = suggested_query
    # Clear the suggested query to prevent it from being processed again
    st.session_state.suggested_query = None
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.write(query)
    
    # Process the query and get bot response
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
    
    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant", avatar="🎓"):
        st.write(bot_reply)

query = st.chat_input("Ask me anything about SRM or any topic...", key="user_chat_input")

if query:
    # Clear input after sending
    st.session_state.chat_input = ""

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.write(query)

    # Bot Logic for regular chat input
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


if query:
    # Clear input after sending
    st.session_state.chat_input = ""

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.write(query)

    # Bot Logic for regular chat input
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


if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👤"):
        st.write(query)

    # Bot Logic for regular chat input
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
st.markdown(f"""
<div class="footer">
    <p style="font-size: 14px; color: {'black' if st.session_state.theme == 'light' else theme['text']};">MIST AI - Powered by Google Gemini | Built for SRM Community</p>
</div>
""", unsafe_allow_html=True)
