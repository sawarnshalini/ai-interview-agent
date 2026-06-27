import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import tempfile

# ---------------- CONFIG ----------------
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found")
    st.stop()

genai.configure(api_key=api_key)

# ✅ SAFE MODEL (WORKING VERSION)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """
You are a professional smartphone interview assistant.

Rules:
- Ask ONE question at a time
- Be natural and conversational
- Keep replies short
"""

INSIGHT_PROMPT = """
You are a market analyst.

Extract:
1. Purchase Drivers
2. Sentiment
3. Product Perception
4. Needs
5. Marketing Insights
"""

# ---------------- VOICE ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        with open(temp_file.name, "rb") as f:
            st.audio(f.read(), format="audio/mp3")

    except:
        pass

# ---------------- UI ----------------
st.set_page_config(page_title="AI Interview", layout="centered")

st.title("🎤 AI Interview Assistant")

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- INPUT ----------------
prompt = st.chat_input("Type here...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    # EXIT FLOW
    if prompt.lower() == "exit":

        full_chat = "\n".join(
            [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
        )

        try:
            result = st.session_state.chat.send_message(
                INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
            )

            st.markdown("## 📊 Insights Report")
            st.write(result.text)

            speak("Here is your report")

        except Exception as e:
            st.error("Failed to generate report")
            st.write(e)

    # NORMAL CHAT
    else:

        try:
            response = st.session_state.chat.send_message(prompt)
            reply = response.text

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            with st.chat_message("assistant"):
                st.write(reply)

            speak(reply[:200])

        except Exception as e:
            st.error("AI error")
            st.write(e)
