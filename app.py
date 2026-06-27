import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import tempfile

# ------------------ CONFIG ------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You are a professional smartphone market research interviewer.

Rules:
- Ask one question at a time
- Ask natural follow-up questions
- Understand purchase behavior
- Understand sentiment
- Keep conversation human and conversational
"""

INSIGHT_PROMPT = """
You are a senior market intelligence analyst.

Analyze the conversation and extract:

1. Purchase Drivers
2. Customer Sentiment (Positive / Neutral / Negative)
3. Product Perception
4. Key Customer Needs
5. Marketing Recommendations

Return structured bullet points in clean format.
"""

# ------------------ TEXT TO SPEECH ------------------
def speak(text):
    try:
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        st.audio(temp_file.name, autoplay=True)
    except:
        pass

# ------------------ UI HEADER ------------------
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
    margin-bottom:20px;
">
👋 Welcome! This AI conducts smartphone consumer interviews and generates market insights automatically.
</div>
""", unsafe_allow_html=True)

# ------------------ SESSION INIT ------------------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

# ------------------ START BUTTON ------------------
if not st.session_state.started:
    if st.button("🚀 Start Interview"):
        st.session_state.started = True

        greeting = "Hi 👋 I'm your AI interview assistant. Let's begin the consumer interview."

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        st.rerun()

    st.stop()

# ------------------ CHAT DISPLAY ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ------------------ USER INPUT ------------------
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

                st.success("Report Generated Successfully ✅")

                st.markdown("## 📊 Market Intelligence Report")
                st.write(result.text)

                speak("Here is your consumer insights report.")

            except Exception:
                st.error("⚠️ Unable to generate report. API limit or error.")

    # ---------------- NORMAL CHAT ----------------
    else:

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking... 🤖"):
                    response = st.session_state.chat.send_message(prompt)
                    reply = response.text
                    st.write(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            speak(reply[:200])

        except Exception:
            error_msg = "⚠️ AI service unavailable or quota exceeded."
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
            st.error(error_msg)
