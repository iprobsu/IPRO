# app.py
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
xNsW0k3aGo4Lsr8LlbQwMt/31UjlNhGYCzS+H72o9MeNV+9v1MmTfOODKDvGmrmO
uyVfNQz1vYlrvg0++h92WlfeknAvOqBAI3JFVNimMcwgzhWKk2CJxfJizcouz9gP
XdE+fZVlgtWFdxF5d7Q5KXF6Xh2YQGNBRV5NWylkB0AOoxzyPcDTt5KHUWSfrzaP
ZhatEfCUQpLYh1WD0WTHJoAluDScosnPlglvqaD16LVGzgMBu/eSAznGoh7zNybh
9NA1s2VqKuQjy0+LMkgBQL5urMTl0OUqpirh0l5RP0tQqpQee1sHQicaHDeETCXk
uu1lAmlTAgMBAAECggEAOm/h23kVLBga9jB6lZ/RkRckpuJGI1GhLyg0EESnLcap
2jDb1OBUX9QraqdUMpIGiRxOwubF3jnFPKCjAILxcOWbxi9ZU1i1ztOjhhqX4TTz
ZvECxui89aP42O3//uodACRKg64hLykilpWiCNCVtsDoRi6/KnBzCFFucf3LhL5T
n7bq2XpObPoxXLRFqRCj0b2PhX56oSzEMJm3BNJno7x1IclJS/yCz9EtlzQPXNEZ
qO1QSPJCE2OtBv8rhUEJxWFlBjgvFLmuLmHnkFmgRIzpWmfNPm1lDNf3r6n6sGKw
zDGMtliSzkxXQMXNp3ferOLZlYu+VE7LOt7tH2+97QKBgQDfmimq64Pk6YmuJKcU
2BHzLDZ1WA7A0b8X1v9cuUZgeLeB/aeXsf6DHi3kgfPZaj7OVVfTrtesxGBwBq53
CA/5PgVfPl/nPVHQtakzfb+5VNN8BLNGFiL44CS3Nhm1YH6fdryr8I1BEdzcW39u
Qq0hByGgHZZTLi48lXiQn2O3BwKBgQDJLud4k5/00a+oO5a9q1HeLTSe1NPEYuKp
G70wGZDKtogZ/BTEqJRjidsaVxk7j2oCIyDlJ4cB+022HdcIOeqWimjGArEG0YsF
pyQIzZL7obL69h2pXCCKdj0v4mc7WlaHMEUIwS2byiaoMeyr3FD1coWYyG/hmVUV
D9QbnLc8VQKBgEa2xHKvZNjiGo6ePNDUvGiBFP/rR08nhh2N+thiJ6Wex7ouc+//
dJQW2UCo8GtTtGUgjFP/uWmD+VO0aTxvqk2SlbRXT5EbzWIJ8Wa9YALGltNj0SZb
HdhDWpkuXNcFm0XnESf3PVTUx1pQ/W3rXEFTtgijEsVfl3PFeYmTPr/FAoGAO4Ec
BZXkYc0DX4cAdukNNeG5BqF8YUG+OLZzpp5pLQwABW+B1QjnmulTXN8WH3+zox4w
xJaEYBmsSolY6J34vL4Db02sfo/LxshA6Dmll7ej8IaLD2SoW0vNnTQhxHRb03B7
erNoggOwm17o2Yw4heBxk1b1gIyRlcEww1n++GECgYBmBuAI+IQVpv9rDbOjnR8H
kOdypsbfWDDBo4RLpxZwnGj7kl/graYkMJQ3oioqNo3P7L7mlTm4dua5kHZV1Nnb
yIoutk7e3kKI7wicf6hNVq1PXvgRQY6lrp5yWdbUSyKpyjdEBn61gRx3Yv1FEPdx
MYODDtd1thtqGAmj/o4DEg==
-----END PRIVATE KEY-----""",
    "client_email": "ipro-dashboard-bot@ipro-project-464106.iam.gserviceaccount.com",
    "client_id": "117954586312861698677",
    "token_uri": "https://oauth2.googleapis.com/token"
}, scopes=SCOPES)

client = gspread.authorize(creds)
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# --- Load and Save ---
def load_data():
    df = pd.DataFrame(worksheet.get_all_records())
    if 'IP Type' in df.columns:
        cols = ['IP Type'] + [c for c in df.columns if c != 'IP Type']
        df = df[cols]
    return df

def save_data(df):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- UI Setup ---
st.set_page_config("📚 IPRO Dashboard", layout="wide")

# --- Login (Hardcoded for now) ---
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
