```python
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

# Gemini Model
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Consumer Interview Assistant",
    page_icon="🎤",
    layout="wide"
)

# ---------------- VOICE FUNCTION ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        with open(temp_file.name, "rb") as f:
            audio = f.read()

        st.audio(audio, format="audio/mp3")
    except:
        pass


# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.big-title {
    font-size: 42px;
    font-weight: bold;
    color: #2563eb;
}

.subtitle {
    font-size: 20px;
    color: gray;
}

.creator {
    font-size: 16px;
    color: #666;
}

.feature {
    background: #f8fafc;
    padding: 18px;
    border-radius: 12px;
    border-left: 5px solid #2563eb;
    margin-bottom: 10px;
}

.footer {
    text-align:center;
    color:gray;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="big-title">
🎤 AI Consumer Interview Assistant
</div>

<div class="subtitle">
Market Research & Consumer Intelligence Platform
</div>

<div class="creator">
👩‍💻 Developed by <b>Shalini Kumari</b>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.title("📌 Project Overview")

    st.success("🤖 AI Powered")

    st.markdown("### Features")

    st.write("""
✅ Voice-enabled interaction

✅ AI consumer interviews

✅ Purchase behavior analysis

✅ Sentiment analysis

✅ Product perception analysis

✅ Market intelligence reporting

✅ Real-time AI conversations
""")

    st.markdown("---")

    st.markdown("### Technology Stack")

    st.write("""
• Python

• Streamlit

• Google Gemini API

• gTTS

• GitHub

• Streamlit Cloud
""")

    st.markdown("---")

    st.info("👩‍💻 Developed by Shalini Kumari")

# ---------------- FEATURE BOXES ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature">
    <h4>🎯 Consumer Research</h4>
    Analyze customer purchase decisions
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature">
    <h4>🤖 AI Interviewing</h4>
    Conduct intelligent interviews
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature">
    <h4>📊 Market Insights</h4>
    Generate actionable business insights
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.info(
    "👋 Hi! I'm your AI Interview Assistant. How can I help you today?"
)

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SHOW CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- USER INPUT ----------------
prompt = st.chat_input("Type your message...")

if prompt:

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    try:
        response = st.session_state.chat.send_message(prompt)

        reply = response.text

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.write(reply)

        # Voice output
        speak(reply[:200])

    except Exception as e:
        st.error("AI error")
        st.write(e)

# ---------------- FOOTER ----------------
st.divider()

st.markdown("""
<div class="footer">
AI Consumer Interview Assistant • Developed by Shalini Kumari • 2026
</div>
""", unsafe_allow_html=True)
```
