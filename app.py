import streamlit as st
import pandas as pd
import os
import altair as alt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Setup ---
def init_state():
    defaults = {
        "logged_in": False,
        "role": None,
        "edit_mode": False,
        "edited_df": None,
        "dark_mode": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# --- Sidebar: Role & Dark Mode Toggle ---
role_color = "#e8eaed" if st.session_state.dark_mode else "#202124"
st.sidebar.markdown(
    f"<span style='color: {role_color}; font-weight:bold;'>🔒 Role: {st.session_state.role}</span>",
    unsafe_allow_html=True
)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=st.session_state.dark_mode)

# --- Dark Mode CSS ---
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
            html, body, [class*="main"] { background-color: #202124 !important; color: #e8eaed !important; }
            [data-testid="stSidebar"], .block-container { background-color: #202124 !important; }
            input, select, textarea { background-color: #303134 !important; color: #e8eaed !important; }
            .stButton > button { background-color: #5f6368 !important; color: #ffffff !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Login ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style='max-width:400px;margin:100px auto;text-align:center;'>
            <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80' style='margin-bottom:20px;' />
            <h2>🔐 IPRO Dashboard Login</h2>
        </div>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pwd == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.experimental_rerun()
            elif user == "mod" and pwd == "mod123":
                st.session_state.logged_in = True
                st.session_state.role = "Moderator"
                st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials")
    st.stop()

# --- Load Data Function ---
def load_data():
    data_dir = "data"
    records = []
    for fname in os.listdir(data_dir):
        if fname.endswith(".xlsx"):
            year = fname[:4]
            path = os.path.join(data_dir, fname)
            xls = pd.read_excel(path, sheet_name=None, engine="openpyxl")
            for sheet, df in xls.items():
                df['Year'] = year
                df['IP Type'] = sheet
                records.append(df)
    df = pd.concat(records, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df:
        df['Author'] = df['Author'].astype(str).str.replace(';',',').str.split(',')
        df['Author'] = df['Author'].apply(lambda lst: [x.strip() for x in lst])
        df = df.explode('Author').reset_index(drop=True)
    return df

df = load_data()

# --- Top Navigation Tabs ---
tabs = st.tabs(["🏠 Home", "📚 Dashboard", "📊 Summary", "⚙️ Admin Tools"])

def home_page():
    st.markdown("""
        <div style='text-align:center;'>
            <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80'/>
            <h1>🏠 Welcome to IP Masterlist System</h1>
            <p>Navigate using the tabs above.</p>
        </div>
    """, unsafe_allow_html=True)

with tabs[0]:
    home_page()

with tabs[1]:
    st.header("📚 IP Dashboard")
    # Place existing dashboard search & filter UI here
    st.markdown("_Dashboard content goes here..._ (Insert your search & filter code)")

with tabs[2]:
    st.header("📊 Summary Statistics")
    filtered = df.copy()
    st.metric("Total Entries", len(filtered))
    if 'IP Type' in filtered:
        st.bar_chart(filtered['IP Type'].value_counts())
    if 'Year' in filtered:
        st.line_chart(filtered['Year'].value_counts().sort_index())

with tabs[3]:
    st.header("⚙️ Admin Tools")
    if st.session_state.role == 'Admin':
        st.markdown("_Admin-only tools will appear here._")
    else:
        st.warning("🔒 Admin access required.")

# --- End of App ---
