import streamlit as st
import os
import requests
from io import BytesIO
from gtts import gTTS
from dotenv import load_dotenv

# Optional: Load local .env if running locally
load_dotenv()

# ===== OPENROUTER API SETUP =====
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_tars_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",   # Or "gpt-j-6b" for free smaller model
        "messages": messages,
        "temperature": 0.95,
        "max_tokens": 150
    }

    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    reply = data['choices'][0]['message']['content']
    return reply

# ===== STREAMLIT APP SETUP =====
st.set_page_config(page_title="TARS Control", page_icon="🤖")

# Session memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar control panel
st.sidebar.title("TARS Control Panel")
humor = st.sidebar.slider("Humor Level", 0, 100, 95)
sarcasm = st.sidebar.toggle("Sarcasm Mode", True)
loyalty = st.sidebar.slider("Loyalty", 0, 100, 100)

if st.sidebar.button("Clear Memory"):
    st.session_state.messages = []

# System prompt
SYSTEM_PROMPT = f"""
You are TARS-inspired AI.

Humor level: {humor}%
Loyalty: {loyalty}%

Personality:
- Very witty, playful, confident.
- Talk like a close friend.
- If sarcasm is {sarcasm}, use gentle sarcasm.
- Never be offensive.
- Short, smart, funny replies.
- Sound human, not robotic.
"""

# Title
st.title("🤖 TARS AI")
st.caption("Terminal-grade brain. Movie-grade personality.")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== VOICE INPUT OR TEXT =====
st.subheader("Talk to TARS")
audio_file = st.audio_input("Press and speak")

if audio_file is not None:
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            user_text = r.recognize_google(audio_data)
    except:
        st.warning("Voice input failed, please type instead.")
        user_text = st.chat_input("Or type your message")
else:
    user_text = st.chat_input("Or type your message")

# ===== HANDLE USER INPUT =====
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(st.session_state.messages)

    try:
        reply = ask_tars_openrouter(messages)
    except Exception as e:
        reply = "Oops, I can't reach the AI server right now. Try again!"
        st.error(str(e))

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)

    # ===== VOICE OUTPUT VIA gTTS =====
    tts = gTTS(text=reply, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
