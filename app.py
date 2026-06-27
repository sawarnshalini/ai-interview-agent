import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import tempfile

# ---------------- CONFIG ----------------
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ⚡ Faster model (IMPORTANT IMPROVEMENT)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """
You are a fast AI consumer interview assistant.

Rules:
- Ask ONE question at a time
- Keep responses short (max 5-6 lines)
- Be natural and conversational
- Focus on smartphone consumer behavior
"""

INSIGHT_PROMPT = """
You are a senior market intelligence analyst.

Extract:
1. Purchase Drivers
2. Customer Sentiment
3. Product Perception
4. Key Customer Needs
5. Marketing Recommendations

Keep output structured and clean.
"""

# ---------------- TEXT TO SPEECH ----------------
def speak(text):
    try:
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        st.audio(temp_file.name)
    except:
        pass

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
👋 Welcome! This AI conducts real-time consumer interviews and generates insights instantly.
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
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

        greeting = "Hi 👋 I'm your AI interview assistant. Let's start the interview."

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        st.rerun()

    st.stop()

# ---------------- CHAT HISTORY ----------------
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
    if prompt.lower() == "exit":

        full_chat = "\n".join(
            [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
        )

        with st.spinner("Generating insights report... 📊"):
            try:
                result = st.session_state.chat.send_message(
                    INSIGHT_PROMPT + "\n\nConversation:\n" + full_chat
                )

                st.success("Report Generated ✅")

                st.markdown("## 📊 Market Intelligence Report")
                st.write(result.text)

            except Exception:
                st.error("⚠️ Failed to generate report (API limit or error)")

    # ---------------- NORMAL CHAT ----------------
    else:

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking... 🤖"):
                    response = st.session_state.chat.send_message(
                        prompt + "\n(Keep response short, max 5-6 lines)"
                    )
                    reply = response.text
                    st.write(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            speak(reply[:150])  # shorter audio = faster UX

        except Exception:
            error_msg = "⚠️ AI temporarily unavailable."
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
            st.error(error_msg)
