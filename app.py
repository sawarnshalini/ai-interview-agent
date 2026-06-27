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
    st.error("❌ GEMINI_API_KEY not found in .env or Streamlit secrets")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

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

# ---------------- TEXT TO SPEECH (FIXED) ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        with open(temp_file.name, "rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format="audio/mp3")

    except Exception:
        st.warning("🔊 Voice unavailable (text only mode)")

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
👋 Welcome! This AI conducts smartphone consumer interviews and generates insights.
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------
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

        greeting = "Hi, I'm your AI interview assistant. Let's begin the interview."

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        st.rerun()

    st.stop()

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

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
                result = model.generate_content(
                    INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
                )
                report = result.text

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

                    response = st.session_state.chat.send_message(
                        prompt + "\nReply in max 5 lines only."
                    )

                    reply = response.text

                    st.write(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            speak(reply[:200])

        except Exception as e:
            error_msg = "⚠️ AI temporarily unavailable. Please try again."
            st.error(error_msg)
            st.write(str(e))
