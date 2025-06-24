import streamlit as st
import pandas as pd
import os
import io
import altair as alt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State ---
for key, default in {
    "logged_in": False,
    "role": None,
    "edit_mode": False,
    "edited_df": None,
    "dark_mode": False,
    "show_summary": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Dark Mode CSS ---
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            html, body, [class*="main"] { background-color: #202124 !important; color: #e8eaed !important; }
            [data-testid="stSidebar"], .block-container { background-color: #202124 !important; }
            input, select, textarea { background-color: #303134 !important; color: #e8eaed !important; }
            .stButton > button { background-color: #5f6368 !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

# --- Summary Page Handler ---
if st.session_state.show_summary:
    # Full-page summary statistics area
    st.markdown("## 📊 Summary Statistics")
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.show_summary = False
        st.experimental_rerun()
    # Load data
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
            df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
            df['Author'] = df['Author'].apply(lambda lst: [x.strip() for x in lst])
            df = df.explode('Author').reset_index(drop=True)
        return df
    df_sum = load_data()
    st.metric("Total Entries", len(df_sum))
    if 'IP Type' in df_sum:
        st.bar_chart(df_sum['IP Type'].value_counts())
    if 'Year' in df_sum:
        st.line_chart(df_sum['Year'].value_counts().sort_index())
    st.stop()

# --- Sidebar ---
role_color = "#e8eaed" if not st.session_state.dark_mode else "#ffffff"
st.sidebar.markdown(f"<span style='color: {role_color};'>🔒 Current Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=st.session_state.dark_mode)

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

# --- Logo & Title ---
st.markdown("""
    <div style='text-align:center;'>
        <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80'/>
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# --- Load Data for Dashboard & Summary ---
def load_dashboard_data():
    data_dir = "data"
    all_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".xlsx"):
            year = filename[:4]
            xls = pd.read_excel(os.path.join(data_dir, filename), sheet_name=None, engine="openpyxl")
            for sheet, df in xls.items():
                df['Year'] = year; df['IP Type'] = sheet
                all_data.append(df)
    df = pd.concat(all_data, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df:
        df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
        df['Author'] = df['Author'].apply(lambda lst: [x.strip() for x in lst])
        df = df.explode('Author').reset_index(drop=True)
    return df

df = load_dashboard_data()

# --- Filters & Dashboard Interface ---
st.markdown("### 🔍 Search Intellectual Property Records")
col1, col2, col3, col4 = st.columns([3,2,2,1])
search_term = col1.text_input("Search by Author or Title")
ip_type = col2.selectbox("Filter by IP Type", ["All"] + sorted(df['IP Type'].unique()))
year = col3.selectbox("Filter by Year", ["All"] + sorted(df['Year'].unique()))
stats_btn = col4.button("📈 View Summary")
with st.expander("📂 Advanced Filters"):
    college = st.selectbox("Filter by College", ["All"] + sorted(df['College'].unique()) if 'College' in df else ["All"])
    campus = st.selectbox("Filter by Campus", ["All"] + sorted(df['Campus'].unique()) if 'Campus' in df else ["All"])
    date_range = st.date_input("Filter by Date Applied", [])

# --- Apply Filters ---
filtered_df = df.copy()
if search_term:
    mask = filtered_df['Author'].astype(str).str.contains(search_term, case=False, na=False) | filtered_df['Title'].astype(str).str.contains(search_term, case=False, na=False)
    filtered_df = filtered_df[mask]
if ip_type != "All": filtered_df = filtered_df[filtered_df['IP Type']==ip_type]
if year != "All": filtered_df = filtered_df[filtered_df['Year']==year]
if college!='All': filtered_df = filtered_df[filtered_df.get('College','')==college]
if campus!='All': filtered_df = filtered_df[filtered_df.get('Campus','')==campus]
if date_range:
    if len(date_range)==1: filtered_df = filtered_df[filtered_df['Date Applied']>=pd.to_datetime(date_range[0])]
    else: filtered_df = filtered_df[filtered_df['Date Applied'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))]

# --- Trigger Summary Page ---
if stats_btn and not filtered_df.empty:
    st.session_state.show_summary = True
    st.experimental_rerun()

# --- Editable Table View ---
if st.session_state.role == "Admin":
    if st.button("✏️ Edit Mode"):
        st.session_state.edit_mode = not st.session_state.edit_mode

if st.session_state.edit_mode:
    st.info("🛠️ Edit Mode: click 'Save Changes' when done.")
    edited = st.data_editor(filtered_df, use_container_width=True)
    if st.button("💾 Save Changes"):
        st.session_state.edited_df = edited; st.success("✅ Saved in session.")
    if st.button("↩️ Cancel"):
        st.session_state.edit_mode=False; st.experimental_rerun()
else:
    st.dataframe(filtered_df, use_container_width=True, height=600)
