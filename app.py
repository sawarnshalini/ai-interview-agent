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

# Use your current working model

model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
page_title="AI Consumer Interview Assistant",
page_icon="🎤",
layout="wide"
)

# ---------------- VOICE ----------------

def speak(text):
try:
tts = gTTS(text=text, lang="en")
temp_file = tempfile.NamedTemporaryFile(
delete=False,
suffix=".mp3"
)
tts.save(temp_file.name)

```
    with open(temp_file.name, "rb") as f:
        audio = f.read()

    st.audio(audio, format="audio/mp3")
except:
    pass
```

# ---------------- CSS ----------------

st.markdown("""

<style>
.main{
    padding-top:1rem;
}

.title{
    font-size:42px;
    font-weight:bold;
    color:#2563eb;
}

.subtitle{
    font-size:20px;
    color:gray;
}

.creator{
    color:#666;
    font-size:16px;
}

.box{
    background:#f8fafc;
    padding:15px;
    border-radius:10px;
    border-left:5px solid #2563eb;
}

.footer{
    text-align:center;
    color:gray;
    font-size:14px;
}
</style>

""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown("""

<div class='title'>
🎤 AI Consumer Interview Assistant
</div>

<div class='subtitle'>
Market Research & Consumer Intelligence Platform
</div>

<div class='creator'>
👩‍💻 Developed by <b>Shalini Kumari</b>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------- SIDEBAR ----------------

with st.sidebar:

```
st.title("📌 Project Overview")

st.success("🤖 AI Powered")

st.markdown("### Features")

st.write("""
```

✅ Voice Interaction

✅ Consumer Interviews

✅ Sentiment Analysis

✅ Purchase Behaviour Analysis

✅ Market Intelligence

✅ AI Insights
""")

```
st.markdown("---")

st.markdown("### Technology Stack")

st.write("""
```

• Python

• Streamlit

• Gemini API

• gTTS

• GitHub

• Streamlit Cloud
""")

```
st.markdown("---")

st.info("Developed by Shalini Kumari")
```

# ---------------- FEATURE BOXES ----------------

col1, col2, col3 = st.columns(3)

with col1:
st.markdown(""" <div class='box'> <h4>🎯 Consumer Research</h4>
Analyze customer preferences </div>
""", unsafe_allow_html=True)

with col2:
st.markdown(""" <div class='box'> <h4>🤖 AI Interviewing</h4>
Intelligent conversations </div>
""", unsafe_allow_html=True)

with col3:
st.markdown(""" <div class='box'> <h4>📊 Market Insights</h4>
Generate business reports </div>
""", unsafe_allow_html=True)

st.divider()

st.info(
"👋 Hi! I'm your AI Interview Assistant. "
"How can I help you today?"
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

# ---------------- INPUT ----------------

prompt = st.chat_input("Type your message...")

if prompt:

```
st.session_state.messages.append(
    {"role":"user","content":prompt}
)

with st.chat_message("user"):
    st.write(prompt)

try:

    response = st.session_state.chat.send_message(prompt)

    reply = response.text

    st.session_state.messages.append(
        {"role":"assistant","content":reply}
    )

    with st.chat_message("assistant"):
        st.write(reply)

    speak(reply[:200])

except Exception as e:
    st.error("AI error")
    st.write(e)
```

# ---------------- FOOTER ----------------

st.divider()

st.markdown("""

<div class='footer'>
AI Consumer Interview Assistant • Developed by Shalini Kumari • 2026
</div>
""", unsafe_allow_html=True)
