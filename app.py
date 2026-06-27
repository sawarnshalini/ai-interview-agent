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
    st.error("❌ GEMINI_API_KEY not found in .env or Streamlit Secrets")
    st.stop()

genai.configure(api_key=api_key)

# ✅ FIXED STABLE MODEL (THIS WORKS MOST CONSISTENTLY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are an AI Interview Assistant for smartphone research.

Rules:
- Ask ONE question at a time
- Be friendly, human-like
- Keep answers short and natural
"""

INSIGHT_PROMPT = """
You are a senior market analyst.

Extract:
- Purchase Drivers
- Customer Sentiment
- Product Perception
- Key Needs
- Marketing Insights
"""

# ---------------- VOICE FIX (IMPORTANT) ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        audio_file = open(temp_file.name, "rb")
        audio_bytes = audio_file.read()
        audio_file.close()

        st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.warning("🔊 Voice not available")
        print("Voice error:", e)

# ---------------- UI ----------------
st.set_page_config(page_title="AI Interview Assistant", layout="centered")

st.markdown("""
# 🎤 AI Interview Assistant  
### 👩‍💻 Built by Shalini Sawarn
""")

st.markdown("""
<div style="
background-color:#111827;
padding:15px;
border-radius:10px;
color:white;
margin-bottom:15px;
">
👋 Hi! I'm your AI Interview Assistant. How can I help you today?
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

# ---------------- START BUTTON ----------------
if not st.session_state.started:
    if st.button("🚀 Start Interview"):
        st.session_state.started = True

        greeting = "Hi 👋 I'm your AI interview assistant. How can I help you today?"

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        # 🔊 FIX: voice now works at start
        speak(greeting)

        st.rerun()

    st.stop()

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- USER INPUT ----------------
prompt = st.chat_input("Type your response...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # ---------------- EXIT ----------------
    if prompt.lower().strip() == "exit":

        full_chat = "\n".join(
            [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
        )

        try:
            result = st.session_state.chat.send_message(
                INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
            )

            report = result.text

            st.markdown("## 📊 Consumer Insights Report")
            st.write(report)

            speak("Here is your consumer insights report")

        except Exception as e:
            st.error("⚠️ Failed to generate report")
            st.write(e)

    # ---------------- NORMAL CHAT ----------------
    else:

        try:
            response = st.session_state.chat.send_message(
                SYSTEM_PROMPT + "\nUser: " + prompt
            )

            reply = response.text

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            with st.chat_message("assistant"):
                st.write(reply)

            # 🔊 FIX: voice restored
            speak(reply[:200])

        except Exception as e:
            st.error("⚠️ AI error")
            st.write(e)
