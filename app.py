import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import tempfile

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You are a professional smartphone market research interviewer.

Rules:
- Ask one question at a time
- Ask natural follow-ups
- Understand purchase behavior
- Understand sentiment
- Keep conversation human and professional
"""

INSIGHT_PROMPT = """
You are a senior market intelligence analyst.

Extract from conversation:
1. Purchase Drivers
2. Customer Sentiment
3. Product Perception
4. Key Customer Needs
5. Marketing Recommendations

Return clean structured bullet points.
"""

# ---------- SPEAK FUNCTION ----------
def speak(text):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    st.audio(temp_file.name, autoplay=True)

# ---------- UI ----------
st.set_page_config(page_title="AI Interview Agent")
st.title("🎤 AI Consumer Interview Assistant")

# ---------- INIT ----------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- DEFAULT GREETING ----------
if "started" not in st.session_state:
    st.session_state.started = True

    greeting = "Hi, I'm your AI interview assistant. How can I help you today?"

    st.session_state.messages.append(
        {"role": "assistant", "content": greeting}
    )

    with st.chat_message("assistant"):
        st.write(greeting)

    speak(greeting)

# ---------- SHOW CHAT ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- INPUT ----------
prompt = st.chat_input("Type your response...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # ---------- EXIT ----------
    if prompt.lower() == "exit":

        try:
            full_chat = "\n".join(
                [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
            )

            result = st.session_state.chat.send_message(
                INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
            )

            st.subheader("📊 Consumer Insights Report")
            st.write(result.text)

            speak("Here is your consumer insights report. Thank you.")

        except Exception as e:
            st.error("⚠️ API limit reached or error occurred. Try again later.")

    else:

        try:
            response = st.session_state.chat.send_message(prompt)
            reply = response.text

        except Exception:
            reply = "⚠️ AI quota reached. Please try again later."

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.write(reply)

        speak(reply[:200])