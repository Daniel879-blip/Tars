
import os
import sqlite3
import hashlib
import base64
import json
import time
from io import BytesIO

import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="TARS AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DB_FILE = "tars_users.db"

# ============================================================
# APP / DEVELOPER INFORMATION
# ============================================================

APP_NAME = "TARS AI"
APP_VERSION = "1.0.0"

DEVELOPER_NAME = "Okeyode Happiness Daniel"
DEVELOPER_PHONE = "09053516260"
DEVELOPER_EMAIL = "happinessd472@gmail.com"

COPYRIGHT_YEAR = "2026"
# ============================================================
# DATABASE / AUTH
# ============================================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memory TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
       )
   """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS archives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            messages TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
        
    conn.commit()
    conn.close()
    
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(name, email, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name.strip(), email.strip().lower(), hash_password(password)),
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists."
    except Exception:
        return False, "Could not create your account."

def create_user(name, email, password):
    # KEEP ALL YOUR EXISTING create_user CODE HERE
    ...


# ============================================================
# MEMORY
# ============================================================

def save_memory(user_id, memory):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "INSERT INTO memories (user_id, memory) VALUES (?, ?)",
        (user_id, memory.strip())
    )

    conn.commit()
    conn.close()


def get_memories(user_id):
    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        "SELECT id, memory FROM memories WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

    conn.close()

    return rows


def delete_memory(memory_id, user_id):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "DELETE FROM memories WHERE id = ? AND user_id = ?",
        (memory_id, user_id)
    )

    conn.commit()
    conn.close()

# ============================================================
# ARCHIVES
# ============================================================

def archive_conversation(user_id, title, messages):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "INSERT INTO archives (user_id, title, messages) VALUES (?, ?, ?)",
        (
            user_id,
            title,
            json.dumps(messages)
        )
    )

    conn.commit()
    conn.close()


def get_archives(user_id):
    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        """
        SELECT id, title, messages, created_at
        FROM archives
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return rows


def delete_archive(archive_id, user_id):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "DELETE FROM archives WHERE id = ? AND user_id = ?",
        (archive_id, user_id)
    )

    conn.commit()
    conn.close()

def authenticate(email, password):
    # KEEP ALL YOUR EXISTING authenticate CODE HERE
    ...

def authenticate(email, password):
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
        (email.strip().lower(), hash_password(password)),
    ).fetchone()
    conn.close()
    return row


init_db()

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "page": "home",
    "theme": "TARS Dark",
    "logged_in": False,
    "user": None,
    "messages": [],
    "show_signup": False,
    "show_login": False,
    "voice_text": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# PREMIUM UI
# ============================================================
st.markdown("""
<style>
/* ============================================================
   TARS THEMES
   ============================================================ */

body:has(.theme-light) .stApp {
    background: #f5f7fb;
    color: #111827;
}

.theme-light {
    background: #f5f7fb;
    color: #111827;
}

.theme-midnight {
    background: #020617;
    color: #f8fafc;
}

.theme-amoled {
    background: #000000;
    color: #ffffff;
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 15%, rgba(76, 125, 255, .16), transparent 30%),
        radial-gradient(circle at 85% 20%, rgba(163, 88, 255, .13), transparent 28%),
        #060811;
    color: #f7f8ff;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

.navbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding: 12px 0 25px;
}

.brand {
    display:flex;
    align-items:center;
    gap:11px;
    font-size:22px;
    font-weight:800;
    letter-spacing:-.5px;
}

.brand-orb {
    width:40px;
    height:40px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#617cff,#a967ff);
    box-shadow:0 0 35px rgba(99,108,255,.4);
}

.hero {
    min-height: 570px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    position:relative;
    overflow:hidden;
}

.hero:before {
    content:"";
    position:absolute;
    width:480px;
    height:480px;
    border-radius:50%;
    background:rgba(91,112,255,.15);
    filter:blur(80px);
    animation:pulse 5s ease-in-out infinite;
}

.ai-orb {
    width:130px;
    height:130px;
    border-radius:38px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:58px;
    background:linear-gradient(145deg,#202b63,#101529);
    border:1px solid rgba(145,158,255,.4);
    box-shadow:
        0 0 0 12px rgba(96,115,255,.05),
        0 0 70px rgba(93,113,255,.34),
        inset 0 0 40px rgba(110,125,255,.12);
    animation:float 4s ease-in-out infinite;
    z-index:1;
}

.hero h1 {
    font-size:clamp(48px,8vw,92px);
    line-height:.95;
    letter-spacing:-5px;
    margin:34px 0 18px;
    z-index:1;
    background:linear-gradient(90deg,#fff,#aebaff,#d6b9ff,#fff);
    background-size:250% auto;
    -webkit-background-clip:text;
    color:transparent;
    animation:shine 5s linear infinite;
}

.hero p {
    max-width:650px;
    color:#9ca5bd;
    font-size:18px;
    line-height:1.7;
    z-index:1;
}

.feature-card {
    background:rgba(18,22,37,.72);
    border:1px solid rgba(255,255,255,.08);
    border-radius:24px;
    padding:27px;
    height:100%;
    backdrop-filter:blur(18px);
    box-shadow:0 15px 50px rgba(0,0,0,.22);
    transition:.25s ease;
}

.feature-card:hover {
    transform:translateY(-5px);
    border-color:rgba(129,145,255,.35);
}

.feature-icon {
    font-size:28px;
    margin-bottom:18px;
}

.feature-card h3 {
    margin:0 0 8px;
    font-size:18px;
}

.feature-card p {
    color:#8f98af;
    line-height:1.6;
    font-size:14px;
}

.auth-shell {
    max-width:500px;
    margin:55px auto;
    background:rgba(15,19,32,.86);
    border:1px solid rgba(255,255,255,.09);
    border-radius:30px;
    padding:36px;
    box-shadow:0 25px 90px rgba(0,0,0,.35);
    backdrop-filter:blur(25px);
}

.auth-title {
    text-align:center;
    font-size:32px;
    font-weight:800;
    margin-bottom:7px;
}

.auth-sub {
    text-align:center;
    color:#8992aa;
    margin-bottom:28px;
}

.chat-top {
    padding:25px 0 18px;
    display:flex;
    align-items:center;
    justify-content:space-between;
}

.chat-title {
    font-size:30px;
    font-weight:800;
}

.status {
    display:inline-flex;
    align-items:center;
    gap:7px;
    color:#91e6b5;
    font-size:13px;
    background:rgba(61,190,120,.09);
    padding:8px 12px;
    border-radius:999px;
    border:1px solid rgba(61,190,120,.18);
}

.dot {
    width:7px;
    height:7px;
    border-radius:50%;
    background:#63e39b;
    box-shadow:0 0 12px #63e39b;
}

@keyframes float {
    0%,100% { transform:translateY(0) rotate(-1deg); }
    50% { transform:translateY(-13px) rotate(1deg); }
}
@keyframes pulse {
    0%,100% { transform:scale(.85); opacity:.55; }
    50% { transform:scale(1.15); opacity:1; }
}
@keyframes shine {
    to { background-position:250% center; }
}
/* ============================================================
   TARS ANIMATION PACK
   ============================================================ */

/* Smooth page entrance */
.stApp {
    animation: pageEnter 0.8s ease-out;
}

@keyframes pageEnter {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* Animated TARS brand orb */
.brand-orb {
    animation:
        brandPulse 3s ease-in-out infinite,
        brandRotate 8s linear infinite;
}

@keyframes brandPulse {
    0%, 100% {
        box-shadow: 0 0 20px rgba(99,108,255,.25);
    }

    50% {
        box-shadow:
            0 0 45px rgba(99,108,255,.65),
            0 0 80px rgba(169,103,255,.25);
    }
}

@keyframes brandRotate {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}


/* AI orb breathing animation */
.ai-orb {
    animation:
        float 4s ease-in-out infinite,
        orbGlow 3s ease-in-out infinite;
}

@keyframes orbGlow {
    0%, 100% {
        filter: brightness(1);
    }

    50% {
        filter: brightness(1.25);
    }
}


/* Feature cards entrance */
.feature-card {
    animation: cardEnter 0.7s ease both;
}

@keyframes cardEnter {
    from {
        opacity: 0;
        transform: translateY(25px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* Different delays make cards appear one after another */
.feature-card:nth-child(1) {
    animation-delay: 0.1s;
}

.feature-card:nth-child(2) {
    animation-delay: 0.2s;
}

.feature-card:nth-child(3) {
    animation-delay: 0.3s;
}


/* Hover effect */
.feature-card:hover {
    transform: translateY(-8px) scale(1.02);
    transition: transform 0.3s ease;
}


/* Buttons */
.stButton > button {
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        filter 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    filter: brightness(1.12);
    box-shadow: 0 10px 30px rgba(99,108,255,.25);
}

.stButton > button:active {
    transform: scale(0.97);
}


/* Chat messages slide in */
[data-testid="stChatMessage"] {
    animation: messageEnter 0.45s ease-out;
}

@keyframes messageEnter {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* Chat input glow */
[data-testid="stChatInput"] {
    animation: inputGlow 4s ease-in-out infinite;
}

@keyframes inputGlow {
    0%, 100% {
        box-shadow: 0 0 0 rgba(99,108,255,0);
    }

    50% {
        box-shadow: 0 0 25px rgba(99,108,255,.12);
    }
}


/* Online status animation */
.status {
    animation: statusPulse 2.5s ease-in-out infinite;
}

@keyframes statusPulse {
    0%, 100% {
        opacity: 1;
    }

    50% {
        opacity: .65;
    }
}


/* Online dot breathing */
.dot {
    animation: dotPulse 1.5s ease-in-out infinite;
}

@keyframes dotPulse {
    0%, 100% {
        transform: scale(1);
        opacity: 1;
    }

    50% {
        transform: scale(1.5);
        opacity: .55;
    }
}


/* Headings appear smoothly */
.hero h1 {
    animation:
        titleEnter 1s ease-out,
        shine 5s linear infinite;
}

@keyframes titleEnter {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* Hero description */
.hero p {
    animation: descriptionEnter 1.2s ease-out;
}

@keyframes descriptionEnter {
    from {
        opacity: 0;
        transform: translateY(15px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* Sidebar entrance */
section[data-testid="stSidebar"] {
    animation: sidebarEnter 0.5s ease-out;
}

@keyframes sidebarEnter {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}


/* Inputs */
.stTextInput input,
.stTextArea textarea {
    transition:
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    transform: scale(1.01);
    box-shadow: 0 0 20px rgba(99,108,255,.15);
}


/* Loading spinner enhancement */
[data-testid="stSpinner"] {
    animation: spinnerFade 0.5s ease-in-out;
}

@keyframes spinnerFade {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}


/* Gentle floating background effect */
.hero:after {
    content: "";
    position: absolute;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    border: 1px solid rgba(130,145,255,.08);
    animation: orbitRing 8s linear infinite;
}

@keyframes orbitRing {
    from {
        transform: rotate(0deg) translateX(170px) rotate(0deg);
    }

    to {
        transform: rotate(360deg) translateX(170px) rotate(-360deg);
    }
}
</style>
""", unsafe_allow_html=True)

#============================================================
# HELPERS
# ============================================================
def ask_tars_openrouter(messages, humor=90, sarcasm=True, loyalty=100):
    if not API_KEY:
        return "Your OpenRouter API key is not configured yet. Add OPENROUTER_API_KEY to your .env file."

    system_prompt = f"""
You are TARS-inspired AI.
Humor: {humor}%.
Loyalty: {loyalty}%.
Sarcasm mode: {sarcasm}.

Personality:
- witty, playful, confident and warm
- sound natural and human
- keep normal answers concise unless the user asks for detail
- use light sarcasm when appropriate
- never be hateful, threatening or genuinely abusive
"""
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.85,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "TARS AI",
    }
    response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        audio = BytesIO()
        tts.write_to_fp(audio)
        encoded = base64.b64encode(audio.getvalue()).decode("utf-8")
        components.html(
            f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{encoded}" type="audio/mp3">
            </audio>
            """,
            height=0,
        )
    except Exception:
        pass

# ============================================================
# WEB SEARCH
# ============================================================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = "https://api.tavily.com/search"


def web_search(query):
    if not TAVILY_API_KEY:
        return "Web search is not configured yet."

    try:
        response = requests.post(
            TAVILY_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "max_results": 5,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        if data.get("answer"):
            results.append(
                f"Search answer:\n{data['answer']}"
            )

        for result in data.get("results", []):
            results.append(
                f"Title: {result.get('title', '')}\n"
                f"Content: {result.get('content', '')}\n"
                f"URL: {result.get('url', '')}"
            )

        return "\n\n".join(results)

    except Exception as exc:
        return f"Web search error: {exc}"

def go(page):
    st.session_state.page = page
    st.session_state.show_signup = False
    st.session_state.show_login = False
    st.rerun()


def top_nav():
    st.markdown("""
    <div class="navbar">
        <div class="brand">
            <div class="brand-orb">🤖</div>
            TARS AI
        </div>
    </div>
    """, unsafe_allow_html=True)
# ============================================================
# HOME
# ============================================================
def home_page():
    top_nav()

    st.markdown("""
    <section class="hero">
        <div class="ai-orb">🤖</div>
        <h1>Your AI.<br>Your TARS.</h1>
        <p>
            A next-generation AI companion with a movie-inspired personality,
            natural conversation, voice interaction and a beautifully designed interface.
        </p>
    </section>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Create free account  →", use_container_width=True, type="primary"):
            st.session_state.show_signup = True
            st.session_state.show_login = False
            st.rerun()
    with c2:
        if st.button("Sign in", use_container_width=True):
            st.session_state.show_login = True
            st.session_state.show_signup = False
            st.rerun()

    st.write("")
    a, b, c = st.columns(3)
    cards = [
        ("🧠", "Smart conversations", "Powered by an AI backend so TARS can answer, reason and chat naturally."),
        ("🎙️", "Talk naturally", "Use your microphone and let TARS respond with voice."),
        ("✨", "Made to feel real", "Animated UI, polished cards, live status and a proper account experience."),
    ]
    for col, (icon, title, desc) in zip((a, b, c), cards):
        with col:
            st.markdown(
                f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
                f'<h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )

    if st.session_state.show_signup:
        signup_form()
    elif st.session_state.show_login:
        login_form()


# ============================================================
# AUTH
# ============================================================
def signup_form():
    st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">Create your account</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Join TARS in a few seconds.</div>', unsafe_allow_html=True)

    name = st.text_input("Full name", placeholder="Your name", key="signup_name")
    email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
    password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="signup_password")
    confirm = st.text_input("Confirm password", type="password", key="signup_confirm")

    if st.button("Create account", use_container_width=True, type="primary"):
        if not name or not email or not password:
            st.error("Please complete all fields.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            ok, message = create_user(name, email, password)
            if ok:
                st.success(message)
                row = authenticate(email, password)
                st.session_state.logged_in = True
                st.session_state.user = row
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.error(message)

    if st.button("Already have an account? Sign in"):
        st.session_state.show_signup = False
        st.session_state.show_login = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def login_form():
    st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Sign in and continue your conversation.</div>', unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="you@example.com", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Your password", key="login_password")

    if st.button("Sign in", use_container_width=True, type="primary"):
        row = authenticate(email, password)
        if row:
            st.session_state.logged_in = True
            st.session_state.user = row
            st.session_state.page = "chat"
            st.rerun()
        else:
            st.error("Incorrect email or password.")

    if st.button("Need an account? Create one"):
        st.session_state.show_login = False
        st.session_state.show_signup = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
# ============================================================
# ABOUT TARS / DEVELOPER PAGE
# ============================================================

def developer_page():

    st.title("🤖 About TARS AI")
    st.caption("Your intelligent AI companion")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🤖 About TARS")

        st.write(
            "TARS AI is a next-generation artificial intelligence "
            "companion designed to provide intelligent, natural and "
            "engaging conversations."
        )

        st.write(
            "TARS can help you learn, create, brainstorm, solve "
            "problems and have everyday conversations."
        )

    with col2:
        st.subheader("👨‍💻 Developer")

        st.image(
            "developer.jpg",
            width=140
        )

        st.write(f"**{DEVELOPER_NAME}**")

        st.write("Creator & Developer of TARS AI.")

        st.write(f"📞 {DEVELOPER_PHONE}")

        st.write(f"📧 {DEVELOPER_EMAIL}")

    st.divider()

    st.subheader("⚙️ App Information")

    st.write(f"**Application:** {APP_NAME}")
    st.write(f"**Version:** {APP_VERSION}")
    st.write("**Status:** Active Development")

    st.divider()

    st.subheader("©️ Copyright")

    st.write(
        f"© {COPYRIGHT_YEAR} {DEVELOPER_NAME}. "
        "All rights reserved."
    )

    st.write(
        "TARS AI, its original branding, interface design and "
        "original application content belong to the developer "
        "unless otherwise stated."
    )

    st.write(
        "Unauthorized copying, reproduction, redistribution, "
        "modification or commercial use of the original application "
        "or its branding is prohibited without permission."
    )

    st.divider()

    if st.button("← Back to TARS", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()


# ============================================================
# CHAT
# ============================================================
def chat_page():
    name = st.session_state.user[1] if st.session_state.user else "User"

    with st.sidebar:
        st.markdown("### 🤖 TARS")
        st.caption(f"Signed in as {name}")
        humor = st.slider("Humor", 0, 100, 90)
        sarcasm = st.toggle("Sarcasm", True)
        loyalty = st.slider("Loyalty", 0, 100, 100)

        if st.button("🗃️ Archive conversation", use_container_width=True):

    if st.session_state.messages:

        user_id = st.session_state.user[0]

        # Use the first user message as the archive title
        title = next(
            (
                msg["content"]
                for msg in st.session_state.messages
                if msg["role"] == "user"
            ),
            "TARS Conversation"
        )

        title = title[:60]

        archive_conversation(
            user_id,
            title,
            st.session_state.messages
        )

        st.session_state.messages = []

        st.success("Conversation archived.")
        st.rerun()

    else:
        st.info("There is no conversation to archive.")


if st.button("＋ New conversation", use_container_width=True):
    st.session_state.messages = []
    st.rerun()


if st.button("🗑️ Clear conversation", use_container_width=True):
    st.session_state.messages = []
    st.rerun()
            
        if st.button("ℹ️ About TARS", use_container_width=True):
           st.session_state.page = "about"
           st.rerun()

        st.divider()
        if st.button("← Sign out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.page = "home"
            st.rerun()

    st.markdown(
        f"""
        <div class="chat-top">
            <div>
                <div class="chat-title">Good to see you, {name.split()[0]}.</div>
                <div style="color:#8e97ad;margin-top:6px;">What are we getting into today?</div>
            </div>
            <div class="status"><span class="dot"></span> TARS online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        x, y, z = st.columns(3)
        suggestions = [
            ("💡", "Give me an idea", "Give me a creative idea for today."),
            ("🧑‍💻", "Help me build", "Help me build a website."),
            ("😂", "Make me laugh", "Tell me something funny."),
        ]
        for col, (icon, title, prompt) in zip((x, y, z), suggestions):
            with col:
                st.markdown(
                    f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
                    f'<h3>{title}</h3><p>{prompt}</p></div>',
                    unsafe_allow_html=True,
                )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Native Streamlit chat input gives a much more app-like experience.
    prompt = st.chat_input("Message TARS…")

    audio_file = st.audio_input("🎙️ Speak to TARS")
    voice_text = ""
    if audio_file is not None:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
            voice_text = recognizer.recognize_google(audio_data)
            st.info(f"Voice message: {voice_text}")
        except Exception:
            st.warning("I couldn't understand that recording. Try again or type your message.")

    message = prompt or voice_text

    if message:
        st.session_state.messages.append({"role": "user", "content": message})

        with st.chat_message("user"):
            st.markdown(message)

        with st.chat_message("assistant"):
            with st.spinner("TARS is thinking…"):
                try:
                    reply = ask_tars_openrouter(
                        st.session_state.messages,
                        humor=humor,
                        sarcasm=sarcasm,
                        loyalty=loyalty,
                    )
                except Exception as exc:
                    reply = "I hit a connection problem. Check your API key and internet connection."
                    st.error(str(exc))

            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        speak(reply)
# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "about":

    developer_page()

elif st.session_state.logged_in and st.session_state.page == "chat":

    chat_page()

else:

    home_page()
