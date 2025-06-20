import streamlit as st
import pandas as pd
import os
import json
import hashlib

# ------------------- CONFIG -------------------
CREDENTIALS_FILE = "users.json"
DEFAULT_USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "mod": {"password": "mod123", "role": "Moderator"}
}

# ------------------- UTILS -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({k: {"password": hash_password(v["password"]), "role": v["role"]}
                       for k, v in DEFAULT_USERS.items()}, f)
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# ------------------- SESSION SETUP -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = None

# ------------------- LOGIN -------------------
if not st.session_state.logged_in:
    st.title("🔐 IPRO Dashboard Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        user = users.get(username)
        if user and user["password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

# ------------------- SIDEBAR NAVIGATION -------------------
st.sidebar.markdown(f"**🔒 Logged in as:** `{st.session_state.username}` ({st.session_state.role})")
navigation = st.sidebar.radio("📁 Menu", ["📊 Dashboard", "⚙️ Settings"])
logout = st.sidebar.button("🚪 Logout")
if logout:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = None
    st.rerun()

# ------------------- MAIN CONTENT -------------------
if navigation == "📊 Dashboard":
    st.title("📚 IP Masterlist Dashboard")
    st.markdown("---")
    st.markdown("🔍 Your dashboard content would continue below here...")

    # Dummy dashboard search content for now
    search_query = st.text_input("Search by Author or Keyword")
    st.write(f"Results for: `{search_query}`")
    # Place your real dashboard logic here

elif navigation == "⚙️ Settings":
    st.title("⚙️ Settings")
    if st.session_state.role == "Admin":
        st.subheader("🔑 Change a User's Password")
        with st.form("change_password"):
            target_user = st.selectbox("Select User", list(users.keys()))
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            update_btn = st.form_submit_button("Update Password")

        if update_btn:
            if new_pw != confirm_pw:
                st.error("❌ Passwords do not match")
            elif not new_pw.strip():
                st.error("❌ Password cannot be empty")
            else:
                users[target_user]["password"] = hash_password(new_pw)
                save_users(users)
                st.success(f"✅ Password for `{target_user}` updated.")
    else:
        st.warning("⚠️ Only Admins can access settings.")
