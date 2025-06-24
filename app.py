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

# --- Sidebar ---
dark_mode_toggle_color = "#e8eaed" if not st.session_state.dark_mode else "#ffffff"
st.sidebar.markdown(f"<span style='color: {dark_mode_toggle_color}'>🔒 Current Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=st.session_state.dark_mode)
dark_mode = st.session_state.dark_mode

# --- Dark Mode Styling (Chrome-like) ---
if dark_mode:
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

# --- Logo and Title ---
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

# --- Filters ---
st.markdown("### 🔍 Search Intellectual Property Records")
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    search_term = st.text_input("Search by Author or Title")
with col2:
    ip_type = st.selectbox("Filter by IP Type", ["All"] + sorted(df['IP Type'].unique()))
with col3:
    year = st.selectbox("Sort by Year", ["All"] + sorted(df['Year'].unique()))
with col4:
    stats_button = st.button("📈")

with st.expander("📂 Advanced Filters"):
    col4, col5, col6 = st.columns(3)
    with col4:
        college = st.multiselect("Filter by College", sorted(df['College'].unique()) if 'College' in df else [])
    with col5:
        campus = st.multiselect("Filter by Campus", sorted(df['Campus'].unique()) if 'Campus' in df else [])
    with col6:
        author_filter = st.multiselect("Filter by Author", sorted(df['Author'].dropna().unique()))

# --- Apply Filters ---
filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[
        filtered_df['Author'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['Title'].astype(str).str.contains(search_term, case=False, na=False)
    ]
if ip_type != "All":
    filtered_df = filtered_df[filtered_df['IP Type'] == ip_type]
if year != "All":
    filtered_df = filtered_df[filtered_df['Year'] == year]
if college:
    filtered_df = filtered_df[filtered_df['College'].isin(college)]
if campus:
    filtered_df = filtered_df[filtered_df['Campus'].isin(campus)]
if author_filter:
    filtered_df = filtered_df[filtered_df['Author'].isin(author_filter)]

# --- Summary Stats Panel ---
if stats_button and not filtered_df.empty:
    st.markdown("## 📊 Summary Statistics Panel")
    tab1, tab2 = st.tabs(["📈 Overall", "🧩 Grouped"])

    with tab1:
        st.metric("Total Records", len(filtered_df))
        st.bar_chart(filtered_df['IP Type'].value_counts())

    with tab2:
        group_by = st.selectbox("Group by", ["Author", "IP Type", "College", "Year"])
        grouped_df = filtered_df.groupby(group_by).size().reset_index(name="Count")
        st.bar_chart(data=grouped_df.set_index(group_by))

# --- Edit Mode Toggle ---
if st.session_state.role == "Admin":
    edit_toggle_col = st.columns([1, 9])[0]
    with edit_toggle_col:
        if st.button("✏️ Edit Mode"):
            st.session_state.edit_mode = not st.session_state.edit_mode

# --- Editable Table View ---
if st.session_state.edit_mode:
    st.info("🛠️ You are now in Edit Mode. Changes will not be saved unless you click 'Save Changes'.")
    edited_df = st.data_editor(filtered_df, use_container_width=True, key="editable_table")

    if st.button("💾 Save Changes"):
        st.session_state.edited_df = edited_df
        st.success("✅ Changes have been saved (in session only).")
    if st.button("↩️ Cancel Changes"):
        st.session_state.edit_mode = False
        st.rerun()
else:
    st.dataframe(filtered_df, use_container_width=True, height=600)
