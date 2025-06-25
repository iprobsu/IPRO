import streamlit as st
import pandas as pd
import os
import altair as alt

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

# --- Dark Mode Styling ---
dark_mode_toggle_color = "#e8eaed" if not st.session_state.dark_mode else "#ffffff"
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            html, body {
                background-color: #202124 !important;
                color: #e8eaed !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            [class*="block-container"], [data-testid="stSidebar"] {
                background-color: #202124 !important;
            }
            input, select, textarea {
                background-color: #303134 !important;
                color: #e8eaed !important;
                border: 1px solid #5f6368 !important;
            }
            label, .stTextInput label, .stSelectbox label, .stDateInput label, .stMultiSelect label {
                color: #e8eaed !important;
            }
            .st-bb, .st-bc, .stMarkdown, .stMarkdown p, .stText, .stTextInput, .stSelectbox, .stDateInput, .css-1v0mbdj, .stMultiSelect {
                color: #e8eaed !important;
            }
            .css-1aumxhk, .css-1v3fvcr, .css-ffhzg2, .stDataFrameContainer, .stDataEditorContainer {
                background-color: #202124 !important;
                color: #e8eaed !important;
            }
            .stCheckbox > label {
                color: #e8eaed !important;
            }
            .stSelectbox > div[data-baseweb="select"] > div {
                background-color: #303134 !important;
            }
            .stButton > button {
                background-color: #5f6368;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Login Page ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style="max-width: 400px; margin: 100px auto; padding: 20px; text-align: center; background: transparent;">
            <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" width="80" style="filter: drop-shadow(0 0 10px #00ffaa); animation: bounce 2s infinite; margin-bottom: 20px;" />
            <h2 style="color: inherit;">🔐 IPRO Dashboard Login</h2>
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

# --- Sidebar Navigation (Permanent) ---
st.sidebar.image("https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png", width=80)
st.sidebar.markdown("<h2 style='text-align: center;'>📚 IPRO Cloud</h2>", unsafe_allow_html=True)

st.sidebar.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            min-width: 250px !important;
            width: 250px !important;
        }
        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

nav_items = {
    "home": "🏠 Home",
    "edit": "✏️ Edit Data",
    "summary": "📊 Summary"
}

if "page" not in st.session_state:
    st.session_state.page = "home"

for key, label in nav_items.items():
    if st.sidebar.button(label):
        st.session_state.page = key

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.session_state.page = 'login'
    st.experimental_rerun()

st.sidebar.markdown(f"<span style='color: {dark_mode_toggle_color}'>🔒 Current Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=st.session_state.dark_mode)

# --- Load Data ---
def load_data():
    files = [f for f in os.listdir("data") if f.endswith(".xlsx")]
    records = []
    for f in files:
        year = f[:4]
        xls = pd.read_excel(os.path.join("data", f), sheet_name=None, engine="openpyxl")
        for sht, df in xls.items():
            df['Year'] = year
            df['IP Type'] = sht
            records.append(df)
    df = pd.concat(records, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df:
        df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
        df['Author'] = df['Author'].apply(lambda x: [a.strip() for a in x])
        df = df.explode('Author').reset_index(drop=True)
    return df

if st.session_state.logged_in:
    df = load_data()

# --- Animated Logo & Title in Center ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" width="80" style="filter: drop-shadow(0 0 10px #00ffaa); animation: bounce 2s infinite;" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    </style>
""", unsafe_allow_html=True)

# --- Page Routing ---
if st.session_state.page == "home":
    st.write("Welcome to the home dashboard! (Home content placeholder)")

elif st.session_state.page == "edit":
    st.write("Edit your data here. (Edit page placeholder)")

elif st.session_state.page == "summary":
    st.write("Summary statistics page. (Summary page placeholder)")
