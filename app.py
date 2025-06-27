# app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
SHEET_ID = "1ACa5R51PWp0Et3cjJZQNyY9hZaIVSVF3k_EqTRoTuj8"
SHEET_NAME = "Sheet1"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ Load credentials from uploaded key file
creds = Credentials.from_service_account_file(
    "ipro-project-464106-723ea01341f2.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def load_data():
    df = pd.DataFrame(worksheet.get_all_records())
    if 'IP Type' in df.columns:
        cols = ['IP Type'] + [c for c in df.columns if c != 'IP Type']
        df = df[cols]
    return df

def save_data(df):
    worksheet.clear()
    worksheet.update([df.columns.tolist()] + df.values.tolist())

# --- UI Setup ---
st.set_page_config("📚 IPRO Dashboard", layout="wide")

# --- Login ---
if "role" not in st.session_state:
    st.session_state.role = None

if not st.session_state.role:
    with st.form("login"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if user == "admin" and pw == "admin123":
                st.session_state.role = "Admin"
            elif user == "mod" and pw == "mod123":
                st.session_state.role = "Moderator"
            else:
                st.error("Invalid login")
    st.stop()

# --- Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "home"

st.sidebar.title("📚 IPRO Navigation")
if st.sidebar.button("🏠 Home (Dashboard)"):
    st.session_state.page = "home"
if st.sidebar.button("✏️ Edit Data"):
    st.session_state.page = "edit"
if st.sidebar.button("🔒 Logout"):
    st.session_state.role = None
    st.experimental_rerun()

# --- Load Data ---
df = load_data()

# --- Home Page ---
if st.session_state.page == "home":
    st.title("📚 IP Masterlist Dashboard")
    st.dataframe(df, use_container_width=True)

# --- Edit Page ---
elif st.session_state.page == "edit":
    if st.session_state.role == "Admin":
        st.title("✏️ Edit Data")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        if st.button("💾 Save Changes"):
            save_data(edited_df)
            st.success("Saved to Google Sheets!")
            st.experimental_rerun()

        if st.button("➕ Add New Column"):
            new_col = st.text_input("Enter new column name:", key="new_col")
            if new_col:
                df[new_col] = ""
                save_data(df)
                st.success(f"Column '{new_col}' added!")
                st.experimental_rerun()
    else:
        st.warning("You must be an Admin to edit data.")

# --- Footer ---
st.markdown("---")
st.markdown(f"🔐 Logged in as: **{st.session_state.role}**")
