import streamlit as st
import pandas as pd
import json
import hashlib
import os

# ---------------------- CONFIG ----------------------
CREDENTIALS_FILE = "users.json"
DEFAULT_USERS = {
    "admin": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "Admin"},
    "mod": {"password": hashlib.sha256("mod123".encode()).hexdigest(), "role": "Moderator"}
}

# ------------------- HELPER FUNCTIONS -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        save_credentials(DEFAULT_USERS)
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=4)

def authenticate(username, password, credentials):
    if username in credentials:
        return credentials[username]["password"] == hash_password(password)
    return False

# ------------------- SESSION SETUP -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

credentials = load_credentials()

# ------------------- LOGIN PAGE -------------------
if not st.session_state.logged_in:
    st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

    st.sidebar.markdown("### 🔐 Login")
    username = st.sidebar.text_input("👤 Username")
    password = st.sidebar.text_input("🔑 Password", type="password")

    if password == "" or username == "":
        st.sidebar.info("ℹ️ Enter credentials to access Admin features.")
        role = "Moderator"
    elif authenticate(username, password, credentials):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = credentials[username]["role"]
        st.experimental_rerun()
    else:
        st.sidebar.error("❌ Incorrect credentials. You are in Moderator (view-only) mode.")
        st.session_state.role = "Moderator"
        st.stop()

# ------------------- LOGGED IN -------------------
role = st.session_state.role
st.sidebar.markdown(f"**🔒 Current Role:** {role}")

# --- Dark Mode Toggle ---
dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=False)

if dark_mode:
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                background-color: #121212 !important;
                color: #e0e0e0 !important;
                font-family: 'Roboto', sans-serif;
            }
            .stTextInput input, .stSelectbox div, .stDateInput input, .stMultiSelect div, .stFileUploader, .stDownloadButton button {
                background-color: #2c2c2c !important;
                color: #ffffff !important;
                border: none !important;
            }
            .element-container .row-widget.stRadio, .stExpanderHeader, .css-1l269bu {
                background-color: #1e1e1e !important;
                color: #ffffff !important;
            }
            .block-container, .sidebar-content, .css-1avcm0n, .css-1d391kg, .stSidebar, .st-emotion-cache-1dj1jju {
                background-color: #121212 !important;
                color: #ffffff !important;
            }
            h1, h2, h3, h4, h5, h6, label, p, .css-10trblm {
                color: #ffffff !important;
            }
            .stButton>button, .stDownloadButton button {
                background-color: #444 !important;
                color: #fff !important;
                border-radius: 5px;
                border: 1px solid #888;
                padding: 0.5em 1em;
                font-size: 1em;
            }
            .stButton>button:hover, .stDownloadButton button:hover {
                background-color: #666 !important;
                color: #fff !important;
            }
            .glow-logo {
                filter: drop-shadow(0 0 10px #00ffaa);
            }
        </style>
    """, unsafe_allow_html=True)

# --- Ghibli Animation Banner ---
st.markdown("""
    <div style="text-align:center; margin-bottom: 1rem;">
        <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjhjZjl6OHY4cW1zZ2s1ZzZvM2MwZHR3dmJncjR4b2l4em5xZW8xcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/JIX9t2j0ZTN9S/giphy.gif" width="100" alt="Totoro Animation">
    </div>
""", unsafe_allow_html=True)

# --- Fonts & Logo Styling ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }
        .glow-logo {
            width: 80px;
            filter: drop-shadow(0 0 8px #00ffaa);
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        h1 {
            text-align: center;
            font-size: 2rem;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Logo and Title ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" class="glow-logo" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# The rest of the original code remains unchanged.
# (Everything after filters, color customization, table display, download buttons, etc.)
