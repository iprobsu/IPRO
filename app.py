import streamlit as st
import json
import hashlib
import os

# ---------------------- CONFIG ----------------------
CREDENTIALS_FILE = "users.json"
DEFAULT_USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "mod": {"password": "mod123", "role": "Moderator"}
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
    st.title("🔐 IPRO Dashboard Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if authenticate(username, password, credentials):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = credentials[username]["role"]
                st.success(f"✅ Welcome, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    st.stop()

# ------------------- LOGGED IN MENU -------------------
st.sidebar.markdown(f"**👋 Logged in as:** `{st.session_state.username}`  ")
st.sidebar.markdown(f"**🔒 Role:** `{st.session_state.role}`")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# ------------------- ADMIN PASSWORD CHANGE -------------------
if st.session_state.role == "Admin":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔑 Change User Password")
    user_to_change = st.sidebar.selectbox("Select User", list(credentials.keys()))
    new_pass = st.sidebar.text_input("New Password", type="password", key="change_pass")
    if st.sidebar.button("🔁 Change Password"):
        credentials[user_to_change]["password"] = hash_password(new_pass)
        save_credentials(credentials)
        st.sidebar.success(f"Password for `{user_to_change}` updated!")

# ------------------- Place your IP dashboard below -------------------

# You can paste your dashboard code here after login is successful.
# Make sure to check st.session_state.role if you want to limit upload/edit to Admins only.

st.title("📚 Welcome to the IP Masterlist Dashboard")
st.write("Your secured data lives here...")
