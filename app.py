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

def change_password(username, old_pw, new_pw, credentials):
    if authenticate(username, old_pw, credentials):
        credentials[username]["password"] = hash_password(new_pw)
        save_credentials(credentials)
        return True
    return False

def reset_users():
    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)
    save_credentials(DEFAULT_USERS)

# ------------------- SESSION SETUP -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# ------------------- LOGIN SCREEN -------------------
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login | IP Masterlist Dashboard", layout="centered")
    credentials = load_credentials()

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
            st.rerun()
        else:
            st.error("❌ Incorrect username or password.")

    if st.button("🔁 Reset to Default Users"):
        reset_users()
        st.success("Users reset to default! Try logging in again.")
    st.stop()

# ------------------- LOGGED IN -------------------
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")
role = st.session_state.role
st.sidebar.markdown(f"**🔒 Current Role:** {role}")

# ------------------- CHANGE PASSWORD -------------------
if st.sidebar.button("🔧 Change Password"):
    with st.sidebar.form("change_pw_form"):
        st.markdown("#### 🔐 Change Your Password")
        old_pw = st.text_input("Old Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Update Password")
        if submitted:
            credentials = load_credentials()
            if new_pw != confirm_pw:
                st.warning("New passwords do not match.")
            elif change_password(st.session_state.username, old_pw, new_pw, credentials):
                st.success("✅ Password successfully changed!")
            else:
                st.error("❌ Incorrect old password.")

# ------------------- DASHBOARD + DATA -------------------
import pandas as pd

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

st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" class="glow-logo" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

st.info(f"Welcome, **{st.session_state.username}**! You are logged in as **{role}**.")
