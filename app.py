import streamlit as st
from google import genai
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

# ✅ NEW GEMINI CLIENT (IMPORTANT FIX)
client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-1.5-flash"

# ---------------- PROMPTS ----------------
SYSTEM_PROMPT = """
You are a professional smartphone market research interviewer.

Rules:
- Ask ONE question at a time
- Keep responses short (max 5-6 lines)
- Be natural and conversational
"""

INSIGHT_PROMPT = """
You are a senior market intelligence analyst.

Extract:
1. Purchase Drivers
2. Customer Sentiment
3. Product Perception
4. Key Customer Needs
5. Marketing Recommendations

Return structured bullet points clearly.
"""

# ---------------- TEXT TO SPEECH ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        with open(temp_file.name, "rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format="audio/mp3")

    except:
        st.warning("🔊 Voice not available")

# ---------------- UI ----------------
st.set_page_config(page_title="AI Interview Agent", layout="centered")

st.markdown("""
# 🎤 AI Consumer Interview Assistant  
### Built by: **Shalini Sawarn**
""")

st.markdown("""
<div style="
    background-color:#111827;
    padding:15px;
    border-radius:10px;
    color:white;
    margin-bottom:15px;
">
👋 Welcome! This AI conducts smartphone consumer interviews and generates insights automatically.
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

        greeting = "Hi 👋 I'm your AI interview assistant. Let's start the interview."

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        st.rerun()

    st.stop()

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- AI CALL FUNCTION ----------------
def get_ai_response(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
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

        try:
            with st.spinner("Generating insights report... 📊"):

                report = get_ai_response(
                    INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
                )

                st.success("Report Generated Successfully ✅")
                st.markdown("## 📊 Market Intelligence Report")
                st.write(report)

                speak("Here is your consumer insights report.")

        except Exception as e:
            st.error("⚠️ Failed to generate report")
            st.write(str(e))

    # ---------------- NORMAL CHAT ----------------
    else:

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking... 🤖"):

                    reply = get_ai_response(
                        prompt + "\nReply in max 5 lines only."
                    )

                    st.write(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            speak(reply[:200])

        except Exception as e:
            st.error("⚠️ AI temporarily unavailable")
            st.write(str(e))
