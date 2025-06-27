# app.py
import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- Google Sheets Setup ---
SHEET_ID = "1ACa5R51PWp0Et3cjJZQNyY9hZaIVSVF3k_EqTRoTuj8"
SHEET_NAME = "Sheet1"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ Upload credentials via sidebar
with st.sidebar.expander("🔑 Upload Service Account JSON"):
    uploaded_file = st.file_uploader("Upload service_account.json", type="json")

if uploaded_file is None:
    st.warning("Please upload your Google service account JSON to proceed.")
    st.stop()

creds = Credentials.from_service_account_info(
    json.load(uploaded_file),
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

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True, resizable=True, filter=True)
        gb.configure_grid_options(domLayout='normal')
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MANUAL,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            height=500,
        )

        updated_df = grid_response["data"]

        if st.button("💾 Save Changes"):
            save_data(updated_df)
            st.success("Saved to Google Sheets!")
            st.experimental_rerun()

        with st.expander("➕ Add New Column"):
            new_col = st.text_input("Enter new column name:")
            if new_col and new_col not in updated_df.columns:
                updated_df[new_col] = ""
                save_data(updated_df)
                st.success(f"Column '{new_col}' added!")
                st.experimental_rerun()
    else:
        st.warning("You must be an Admin to edit data.")

# --- Footer ---
st.markdown("---")
st.markdown(f"🔐 Logged in as: **{st.session_state.role}**")
