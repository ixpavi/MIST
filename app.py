import streamlit as st
from better_profanity import profanity
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Load profanity filter
profanity.load_censor_words()

# Streamlit page configuration
st.set_page_config(page_title="MIST AI - SRM Assistant", page_icon="🎓", layout="centered")

# SRM Header
st.markdown("<h1 style='text-align:center; color:#800000;'>🎓 MIST AI - SRM Virtual Assistant</h1>", unsafe_allow_html=True)
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

        INSTRUCTIONS:
        1. Always relate your responses to SRM University context, even for general topics
        2. Be specific about SRM programs, facilities, departments, or campus life when possible
        3. If asked about general topics, connect them to SRM student experience
        4. For official queries (admissions, fees), provide helpful info but suggest contacting SRM directly for latest details
        5. Keep responses informative yet conversational (100-200 words typically)
        6. Use a friendly, helpful tone like a knowledgeable SRM student or staff member

        EXAMPLES:
        - "computer science" → Talk about CSE department at SRM, curriculum, faculty, placements, labs
        - "food" → Discuss SRM dining halls, mess facilities, popular food spots near campus
        - "weather" → Mention Chennai climate and how it affects SRM campus life, what to bring
        - "sports" → Describe SRM sports facilities, teams, tournaments, fitness centers
        - "artificial intelligence" → Explain AI/ML programs in SRM, research opportunities, faculty expertise

        Question: {query}

        Provide a helpful SRM-focused response:
        """
        
        response = model.generate_content(prompt)
        return response.text if response.text else "I couldn't generate a response. Please try again!"
        
    except Exception as e:
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
    
    # Handle simple greetings without API call (save API usage)
    elif query.lower().strip() in ["hi", "hello", "hey", "sup", "what's up"]:
        bot_reply = "Hello! 😊 I'm MIST AI, your SRM assistant. I can help you with anything about SRM University or answer general questions in the SRM context. What would you like to know?"
    
    # Handle basic bot info queries
    elif any(phrase in query.lower() for phrase in ["who are you", "what can you do", "what are you", "help me"]):
        bot_reply = "I'm MIST AI, your virtual assistant for SRM Institute of Science and Technology! 🎓\n\nI can help you with:\n• SRM admissions, courses, and departments\n• Campus facilities and student life\n• General questions answered in SRM context\n• Academic programs and opportunities\n\nJust ask me anything!"
    
    # Handle thank you messages
    elif any(phrase in query.lower() for phrase in ["thank you", "thanks", "thx"]):
        bot_reply = "You're very welcome! 😊 Feel free to ask me anything else about SRM or any other topic. I'm here to help!"
    
    # Let Gemini handle everything else in SRM context
    else:
        # Check cache first to save API calls
        cache_key = query.lower().strip()
        if cache_key in st.session_state.response_cache:
            bot_reply = st.session_state.response_cache[cache_key]
        else:
            # Show loading indicator
            with st.spinner("Let me think about that in SRM context..."):
                bot_reply = get_srm_response(query)
                # Cache the response
                st.session_state.response_cache[cache_key] = bot_reply

    # Show bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666; font-size:12px;'>MIST AI - Powered by Google Gemini | Built for SRM Community</p>", unsafe_allow_html=True)
