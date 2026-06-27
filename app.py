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

# ✅ SAFE MODEL (NO 404 ISSUES)
model = genai.GenerativeModel("gemini-pro")

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are an AI Interview Assistant for smartphone research.

Rules:
- Ask ONE question at a time
- Be friendly and conversational
- Keep responses short (max 5-6 lines)
"""

# ---------------- INSIGHT PROMPT ----------------
INSIGHT_PROMPT = """
You are a market intelligence analyst.

Extract:
- Purchase Drivers
- Customer Sentiment
- Product Perception
- Key Needs
- Marketing Insights
"""

# ---------------- TEXT TO SPEECH FIX ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        with open(temp_file.name, "rb") as f:
            audio = f.read()

        st.audio(audio, format="audio/mp3")

    except Exception as e:
        st.warning("🔊 Voice not available")
        print(e)

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
👋 Welcome! I’m your AI Interview Assistant.  
How can I help you today?
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

# ---------------- START BUTTON ----------------
if not st.session_state.started:
    if st.button("🚀 Start Interview"):
        st.session_state.started = True

        greeting = "Hi 👋 I'm your AI assistant. How can I help you today?"

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        speak(greeting)
        st.rerun()

    st.stop()

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- AI FUNCTION ----------------
def get_response(prompt):
    response = model.generate_content(prompt)
    return response.text

# ---------------- USER INPUT ----------------
prompt = st.chat_input("Type your response...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # ---------------- EXIT FLOW ----------------
    if prompt.lower().strip() == "exit":

        full_chat = "\n".join(
            [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
        )

        with st.spinner("Generating report... 📊"):

            report = get_response(
                INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
            )

            st.success("Report Generated ✅")
            st.markdown("## 📊 Insights Report")
            st.write(report)

            speak("Here is your consumer insights report")

    # ---------------- NORMAL CHAT ----------------
    else:

        with st.spinner("Thinking... 🤖"):

            reply = get_response(
                SYSTEM_PROMPT + "\nUser: " + prompt + "\nAI:"
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.write(reply)

        speak(reply[:200])
