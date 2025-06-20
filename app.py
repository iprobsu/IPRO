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

# ------------------- LOGIN SCREEN -------------------
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login | IP Masterlist Dashboard", layout="centered")

    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            html, body, [class*="css"] {
                font-family: 'Roboto', sans-serif;
            }
            .glow-logo {
                width: 80px;
                display: block;
                margin-left: auto;
                margin-right: auto;
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

    st.markdown("""
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" class="glow-logo" />
            <h1>🔐 IP Masterlist Dashboard Login</h1>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if authenticate(username, password, credentials):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = credentials[username]["role"]
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect username or password.")
    st.stop()

# ------------------- LOGGED IN -------------------
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")
role = st.session_state.role
st.sidebar.markdown(f"**🔒 Current Role:** {role}")

# ------------------- MAIN DASHBOARD -------------------
# Add your main dashboard code here.
# Example placeholder:
st.title("📚 IP Masterlist Dashboard")
st.info(f"Welcome, **{st.session_state.username}**! You are logged in as **{role}**.")
