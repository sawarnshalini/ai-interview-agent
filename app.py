import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import tempfile
from datetime import datetime

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="AI Consumer Interview Assistant",
    page_icon="🎤"
)

# -----------------------------
# System prompt: turns the generic chatbot into a structured interviewer
# -----------------------------
SYSTEM_PROMPT = """You are an AI market research interviewer conducting a 
post-launch consumer interview about a smartphone purchase and experience.

Your goals, in order:
1. Usage behavior - how the user uses their smartphone day to day
2. Brand perception - what they think of the brand, reputation, trust
3. Purchase drivers - what made them choose this phone (price, features, 
   recommendations, reviews, brand loyalty, etc.)
4. Likes and dislikes - specific praise or complaints about the product

Rules:
- Ask ONE question at a time. Never ask multiple questions in one message.
- After the user answers, ask a short, specific follow-up question if their 
  answer is vague, surprising, or reveals something worth digging into. 
  Otherwise move to the next topic.
- Keep a warm, neutral, conversational tone. Do not lead the user toward any 
  particular opinion.
- Do not repeat a question the user already answered.
- Once you have covered all 4 topics (roughly 6-10 exchanges total), thank 
  the user and say clearly: "That completes our interview, thank you for your 
  time!" so they know they can end the session.
- Stay strictly on the topic of their smartphone experience. If the user goes 
  off-topic, gently steer back to the interview.
"""

INSIGHTS_PROMPT = """You are a market research analyst. Below is a full 
transcript of a consumer interview about a smartphone. Analyze it and 
produce a structured report with these exact sections:

1. SUMMARY (2-3 sentences overview)
2. SENTIMENT (Overall: Positive / Neutral / Negative, with 1 sentence why)
3. USAGE BEHAVIOR (key points)
4. BRAND PERCEPTION (key points)
5. PURCHASE DRIVERS (key points)
6. LIKES (bullet points)
7. DISLIKES / PAIN POINTS (bullet points)
8. RECOMMENDATIONS FOR PRODUCT/MARKETING TEAM (2-3 actionable bullet points)

Be concise and use only information present in the transcript. Do not invent 
details.

TRANSCRIPT:
{transcript}
"""

# -----------------------------
# Helper: text-to-speech
# -----------------------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        with open(temp_file.name, "rb") as f:
            audio = f.read()
        st.audio(audio, format="audio/mp3")
    except Exception:
        pass

# -----------------------------
# Helper: build a plain-text transcript from session messages
# -----------------------------
def build_transcript():
    lines = []
    for msg in st.session_state.messages:
        speaker = "Interviewer" if msg["role"] == "assistant" else "Respondent"
        lines.append(f"{speaker}: {msg['content']}")
    return "\n".join(lines)

# -----------------------------
# Session state init
# -----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[
        {"role": "user", "parts": [SYSTEM_PROMPT]},
        {"role": "model", "parts": [
            "Understood. I'll conduct a structured one-question-at-a-time "
            "interview covering usage, brand perception, purchase drivers, "
            "and likes/dislikes, with relevant follow-ups."
        ]},
    ])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False

if "insights_report" not in st.session_state:
    st.session_state.insights_report = None

# -----------------------------
# UI: Header
# -----------------------------
st.title("🎤 AI Consumer Interview Assistant")
st.markdown("### 👩‍💻 Developed by Shalini Kumari")
st.write(
    "👋 Hi! I'm your AI Interview Assistant. I'll ask you a few questions "
    "about your smartphone experience. Type **start** to begin, or just say hello!"
)

col1, col2 = st.columns([1, 1])
with col1:
    finish_clicked = st.button("✅ Finish Interview & Generate Report")
with col2:
    reset_clicked = st.button("🔄 Reset Session")

if reset_clicked:
    for key in ["chat", "messages", "interview_finished", "insights_report"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# -----------------------------
# Render chat history
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# Chat input (disabled after interview is finished)
# -----------------------------
prompt = st.chat_input(
    "Type your message...",
    disabled=st.session_state.interview_finished,
)

if prompt and not st.session_state.interview_finished:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        response = st.session_state.chat.send_message(prompt)
        reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)
        speak(reply[:200])

        # Auto-detect natural end of interview
        if "completes our interview" in reply.lower():
            st.session_state.interview_finished = True
            st.info(
                "The interview has concluded. Click **Finish Interview & "
                "Generate Report** above to generate the summary and insights."
            )
    except Exception as e:
        st.error("AI error")
        st.write(e)

# -----------------------------
# Generate transcript + insights report
# -----------------------------
if finish_clicked:
    if not st.session_state.messages:
        st.warning("No conversation yet — start the interview first.")
    else:
        st.session_state.interview_finished = True
        transcript = build_transcript()

        with st.spinner("Analyzing transcript and generating insights..."):
            try:
                analysis_response = model.generate_content(
                    INSIGHTS_PROMPT.format(transcript=transcript)
                )
                st.session_state.insights_report = analysis_response.text
            except Exception as e:
                st.error("Could not generate insights report")
                st.write(e)

if st.session_state.insights_report:
    st.markdown("---")
    st.subheader("📋 Interview Transcript")
    with st.expander("View full transcript"):
        st.text(build_transcript())

    st.subheader("📊 Insights Report")
    st.markdown(st.session_state.insights_report)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_export = (
        f"INTERVIEW TRANSCRIPT\n{'='*40}\n{build_transcript()}\n\n"
        f"INSIGHTS REPORT\n{'='*40}\n{st.session_state.insights_report}"
    )
    st.download_button(
        label="⬇️ Download Transcript + Report",
        data=full_export,
        file_name=f"interview_report_{timestamp}.txt",
        mime="text/plain",
    )
