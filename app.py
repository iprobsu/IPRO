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
            label {
                color: #e8eaed !important;
            }
            .stDataFrameContainer, .stDataEditorContainer {
                background-color: #202124 !important;
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

# --- Main Filter Panel ---
st.markdown("## 🎛️ Filter Intellectual Property Records")
col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_authors = st.multiselect("Filter by Author", sorted(df['Author'].dropna().unique()))
with col2:
    selected_colleges = st.multiselect("Filter by College", sorted(df['College'].dropna().unique()) if 'College' in df else [])
with col3:
    selected_iptypes = st.multiselect("Filter by IP Type", sorted(df['IP Type'].dropna().unique()))
with col4:
    selected_years = st.multiselect("Filter by Year", sorted(df['Year'].dropna().unique()))

# --- Apply Combined Filters ---
filtered_df = df.copy()
if selected_authors:
    filtered_df = filtered_df[filtered_df['Author'].isin(selected_authors)]
if selected_colleges:
    filtered_df = filtered_df[filtered_df['College'].isin(selected_colleges)]
if selected_iptypes:
    filtered_df = filtered_df[filtered_df['IP Type'].isin(selected_iptypes)]
if selected_years:
    filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]

# --- Summary Panel ---
st.markdown("## 📊 Summary of Filtered Data")
if not filtered_df.empty:
    st.metric("Total Records", len(filtered_df))

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Unique Authors", filtered_df['Author'].nunique())
    with kpi2:
        st.metric("Colleges Involved", filtered_df['College'].nunique())
    with kpi3:
        st.metric("Years Covered", filtered_df['Year'].nunique())

    chart1, chart2 = st.columns(2)
    with chart1:
        st.altair_chart(alt.Chart(filtered_df).mark_bar().encode(
            x='IP Type', y='count()', color='IP Type', tooltip=['IP Type', 'count()']
        ).properties(title="IP Type Distribution"), use_container_width=True)

        if 'College' in filtered_df:
            st.altair_chart(alt.Chart(filtered_df).mark_arc().encode(
                theta='count()', color='College', tooltip=['College', 'count()']
            ).properties(title="College Contribution"), use_container_width=True)

    with chart2:
        if 'Year' in filtered_df:
            year_df = filtered_df['Year'].value_counts().reset_index()
            year_df.columns = ['Year', 'Count']
            st.altair_chart(alt.Chart(year_df).mark_line(point=True).encode(
                x='Year', y='Count', tooltip=['Year', 'Count']
            ).properties(title="Submissions Over Time"), use_container_width=True)

        if 'Author' in filtered_df:
            top_authors = filtered_df['Author'].value_counts().nlargest(5).reset_index()
            top_authors.columns = ['Author', 'Count']
            st.altair_chart(alt.Chart(top_authors).mark_bar().encode(
                x='Count', y=alt.Y('Author', sort='-x'), tooltip=['Author', 'Count']
            ).properties(title="Top Authors"), use_container_width=True)
else:
    st.warning("No data matches your filter selection.")
