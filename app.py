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
    st.title("🔐 IP Masterlist Dashboard Login")

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
