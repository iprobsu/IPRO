import streamlit as st
import pandas as pd
import os
import io
import altair as alt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "edited_df" not in st.session_state:
    st.session_state.edited_df = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# --- Sidebar Fix ---
role_color = "#e8eaed" if st.session_state.dark_mode else "#202124"
st.sidebar.markdown(f"<span style='color: {role_color}; font-weight: bold;'>🔒 Current Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.sidebar.markdown(f"<label style='color: {role_color};'>🌗 Enable Dark Mode</label>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("", value=st.session_state.dark_mode)
dark_mode = st.session_state.dark_mode

st.sidebar.markdown("---")
if st.sidebar.button("📚 Dashboard"):
    st.session_state.page = "dashboard"
if st.sidebar.button("📈 Summary Statistics"):
    st.session_state.page = "summary"

# --- Dark Mode Styling ---
if dark_mode:
    st.markdown("""
        <style>
            html, body, [class*="main"] {
                background-color: #202124 !important;
                color: #e8eaed !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            [data-testid="stSidebar"], .block-container {
                background-color: #202124 !important;
            }
            input, select, textarea {
                background-color: #303134 !important;
                color: #e8eaed !important;
                border: 1px solid #5f6368 !important;
            }
            label, .stTextInput label, .stSelectbox label, .stDateInput label,
            .stMultiSelect label, .stCheckbox label {
                color: #e8eaed !important;
            }
            .st-bb, .st-bc, .stMarkdown, .stMarkdown p,
            .stText, .stDataFrame, .css-1v0mbdj {
                color: #e8eaed !important;
            }
            .stButton > button {
                background-color: #5f6368 !important;
                color: #ffffff !important;
                border: none;
            }
            .stSelectbox > div[data-baseweb="select"] > div {
                background-color: #303134 !important;
            }
            .stExpanderHeader {
                color: #e8eaed !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Login Page ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style='max-width: 400px; margin: 100px auto; padding: 20px; text-align: center;'>
            <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80' style='filter: drop-shadow(0 0 10px #00ffaa); animation: bounce 2s infinite; margin-bottom: 20px;' />
            <h2>🔐 IPRO Dashboard Login</h2>
        </div>
        <style>
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
        </style>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.rerun()
            elif username == "mod" and password == "mod123":
                st.session_state.logged_in = True
                st.session_state.role = "Moderator"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    st.stop()

# --- Load Data ---
def load_data():
    data_dir = "data"
    all_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".xlsx"):
            year = filename[:4]
            path = os.path.join(data_dir, filename)
            xls = pd.read_excel(path, sheet_name=None, engine="openpyxl")
            for sheet_name, df in xls.items():
                df["Year"] = year
                df["IP Type"] = sheet_name
                df["Source File"] = filename
                all_data.append(df)
    df = pd.concat(all_data, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df['Date Approved'] = pd.to_datetime(df.get('Date Approved', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df.columns:
        df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
        df['Author'] = df['Author'].apply(lambda x: [a.strip() for a in x])
        df = df.explode('Author').reset_index(drop=True)
    return df

df = load_data()

# You can now insert page routing logic here using st.session_state.page ("dashboard" vs "summary")...
