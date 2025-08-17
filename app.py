import gradio as gr
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

# -------------------- Chat Function --------------------
def chat(message, history):
    # Censor bad words
    clean_message = profanity.censor(message)

    try:
        # Get response from Gemini
        response = model.generate_content(clean_message)
        bot_reply = response.text if response else "Sorry, I couldn't generate a reply."
    except Exception as e:
        bot_reply = f"⚠️ Error: {str(e)}"

    return bot_reply

# -------------------- Gradio UI --------------------
with gr.Blocks(theme="default") as demo:  # 🔆 Light theme by default
    gr.Markdown("## 🤖 Gemini Chatbot")
    gr.Markdown("Chat with a Gemini-powered AI. Profanity will be censored automatically.")

    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(placeholder="Type your message here...")
    clear = gr.Button("Clear Chat")

    def user_message(user_input, chat_history):
        bot_reply = chat(user_input, chat_history)
        chat_history.append((user_input, bot_reply))
        return "", chat_history

    msg.submit(user_message, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()

