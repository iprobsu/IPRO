import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
SHEET_ID = "1ACa5R51PWp0Et3cjJZQNyY9hZaIVSVF3k_EqTRoTuj8"
SHEET_NAME = "Sheet1"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info({
    "type": "service_account",
    "project_id": "ipro-project-464106",
    "private_key_id": "723ea01341f200401176f9115d2613d7318185db",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCvuQKYHG7flATX
...your full private key here...
-----END PRIVATE KEY-----""",
    "client_email": "ipro-dashboard-bot@ipro-project-464106.iam.gserviceaccount.com",
    "client_id": "117954586312861698677",
    "token_uri": "https://oauth2.googleapis.com/token"
}, scopes=SCOPES)

client = gspread.authorize(creds)
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# --- Data Load/Save ---
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

if "role" not in st.session_state:
    st.session_state.role = None
if not st.session_state.role:
    with st.form("login"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
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
if st.sidebar.button("🏠 Home"):
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
        st.title("✏️ Excel-style Editing (Admin Only)")
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="editable_table"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 Save Changes"):
                save_data(edited_df)
                st.success("Changes saved to Google Sheets!")
                st.experimental_rerun()

        with col2:
            new_col = st.text_input("➕ Add New Column", key="new_column_input")
            if st.button("Add Column"):
                if new_col and new_col not in df.columns:
                    df[new_col] = ""
                    save_data(df)
                    st.success(f"Column '{new_col}' added!")
                    st.experimental_rerun()
                elif new_col in df.columns:
                    st.warning("Column already exists.")
                else:
                    st.warning("Enter a valid column name.")
    else:
        st.warning("You must be an Admin to edit data.")

# --- Footer ---
st.markdown("---")
st.markdown(f"🔐 Logged in as: **{st.session_state.role}**")
