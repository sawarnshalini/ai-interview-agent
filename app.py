import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import tempfile

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def speak(text):
try:
tts = gTTS(text=text, lang="en")
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
tts.save(temp_file.name)

```
    with open(temp_file.name, "rb") as f:
        audio = f.read()

    st.audio(audio, format="audio/mp3")
except:
    pass
```

st.set_page_config(
page_title="AI Consumer Interview Assistant",
page_icon="🎤"
)

st.title("🎤 AI Consumer Interview Assistant")
st.markdown("### 👩‍💻 Developed by Shalini Kumari")
st.write("👋 Hi! I'm your AI Interview Assistant. How can I help you today?")

if "chat" not in st.session_state:
st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
st.session_state.messages = []

for msg in st.session_state.messages:
with st.chat_message(msg["role"]):
st.write(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:

```
st.session_state.messages.append(
    {
        "role": "user",
        "content": prompt
    }
)

with st.chat_message("user"):
    st.write(prompt)

try:
    response = st.session_state.chat.send_message(prompt)

    reply = response.text

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    with st.chat_message("assistant"):
        st.write(reply)

    speak(reply[:200])

except Exception as e:
    st.error("AI error")
    st.write(e)
```
