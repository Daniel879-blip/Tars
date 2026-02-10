import streamlit as st
import os
import requests
from io import BytesIO
from gtts import gTTS
import base64
import streamlit.components.v1 as components
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

# Create a text input bar and a send button
user_text = st.text_input("Type your message here...", key="user_input")
send_button = st.button("Send")

if send_button and user_text:
    # Append user message to session memory
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    with st.chat_message("user"):
        st.markdown(user_text)

    # Build messages for AI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(st.session_state.messages)

    # Get AI reply from OpenRouter
    try:
        reply = ask_tars_openrouter(messages)
    except Exception as e:
        reply = "Oops, I can't reach the AI server right now. Try again!"
        st.error(str(e))

    # Append AI reply to memory and display
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # ===== AUTO SPEAK REPLY VIA gTTS + JS =====
    tts = gTTS(text=reply, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")
    components.html(f"""
    <audio id="audio" autoplay>
      <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    <script>
      var audio = document.getElementById('audio');
      audio.play();
    </script>
    """, height=0)

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

    # ===== AUTO SPEAK REPLY VIA gTTS + JS =====
    tts = gTTS(text=reply, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    # Encode audio to base64 and autoplay
    audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")
    components.html(f"""
    <audio id="audio" autoplay>
      <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    <script>
      var audio = document.getElementById('audio');
      audio.play();
    </script>
    """, height=0)
