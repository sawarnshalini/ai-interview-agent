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
    st.error("❌ GEMINI_API_KEY missing")
    st.stop()

genai.configure(api_key=api_key)

# ✅ AUTO-SELECT WORKING MODEL (THIS FIXES 404 ISSUE PERMANENTLY)
def get_model():
    models = [m.name for m in genai.list_models()]

    # prefer best available model automatically
    for preferred in [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-pro"
    ]:
        if preferred in models:
            return genai.GenerativeModel(preferred)

    # fallback: first generative model available
    for m in models:
        if "generateContent" in str(genai.get_model(m).supported_generation_methods):
            return genai.GenerativeModel(m)

    raise Exception("No compatible Gemini model found")

model = get_model()

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
st.title("🎤 AI Interview Assistant")
st.markdown("### 👩‍💻 Built by Shalini Sawarn")

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- INPUT ----------------
prompt = st.chat_input("Type your response...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

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
