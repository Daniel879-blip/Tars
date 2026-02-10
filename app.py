import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

st.set_page_config(page_title="TARS Control", page_icon="🤖")

# ========== SESSION MEMORY ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== SIDEBAR CONTROL PANEL ==========
st.sidebar.title("TARS Control Panel")

humor = st.sidebar.slider("Humor Level", 0, 100, 95)
sarcasm = st.sidebar.toggle("Sarcasm Mode", True)
loyalty = st.sidebar.slider("Loyalty", 0, 100, 100)

if st.sidebar.button("Clear Memory"):
    st.session_state.messages = []

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

# ========== TITLE ==========
st.title("🤖 TARS AI")
st.caption("Terminal-grade brain. Movie-grade personality.")

# ========== SHOW CHAT ==========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========== VOICE INPUT ==========
st.subheader("Talk to TARS")
audio_file = st.audio_input("Press and speak")

if audio_file is not None:
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file
    )
    user_text = transcript.text
else:
    user_text = st.chat_input("Or type your message")

# ========== HANDLE USER INPUT ==========
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(st.session_state.messages)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.95,
        max_tokens=120
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)

    # ========== LOUD VOICE OUTPUT ==========
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=reply
    )

    st.audio(speech.read(), format="audio/mp3", autoplay=True)
