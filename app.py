import streamlit as st
import pandas as pd
import os
import altair as alt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Defaults ---
def init_state():
    defaults = {
        "logged_in": False,
        "role": None,
        "edit_mode": False,
        "edited_df": None,
        "dark_mode": False,
        "show_summary": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

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

# --- Authentication ---
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
                st.session_state.logged_in = True; st.session_state.role = "Admin"; st.experimental_rerun()
            elif user == "mod" and pwd == "mod123":
                st.session_state.logged_in = True; st.session_state.role = "Moderator"; st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials")
    st.stop()

# --- Sidebar ---
role_color = "#e8eaed" if st.session_state.dark_mode else "#202124"
st.sidebar.markdown(f"<span style='color:{role_color};font-weight:bold;'>🔒 Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Dark Mode", value=st.session_state.dark_mode)

# --- Data Loader ---
def load_data():
    files = [f for f in os.listdir('data') if f.endswith('.xlsx')]
    records = []
    for f in files:
        yr = f[:4]
        sheets = pd.read_excel(os.path.join('data',f), sheet_name=None, engine='openpyxl')
        for sht,df in sheets.items():
            df['Year']=yr; df['IP Type']=sht
            records.append(df)
    df = pd.concat(records, ignore_index=True)
    df['Date Applied']=pd.to_datetime(df.get('Date Applied',pd.NaT),errors='coerce')
    df.fillna('',inplace=True)
    if 'Author' in df:
        df['Author']=df['Author'].astype(str).str.replace(';',',').str.split(',')
        df['Author']=df['Author'].apply(lambda L:[x.strip() for x in L])
        df=df.explode('Author').reset_index(drop=True)
    return df

df = load_data()

# --- Summary Full Page ---
if st.session_state.show_summary:
    st.markdown("## 📊 Summary Statistics")
    if st.button("← Back to Dashboard"):
        st.session_state.show_summary=False; st.experimental_rerun()
    st.metric("Total Records", len(df))
    st.metric("Distinct IP Types", df['IP Type'].nunique())
    if 'IP Type' in df:
        st.bar_chart(df['IP Type'].value_counts())
    if 'Year' in df:
        counts = df['Year'].value_counts().sort_index()
        st.line_chart(counts)
    st.stop()

# --- Main Dashboard UI ---
# Logo & Title
st.markdown("""
  <div style='text-align:center;'>
    <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80'/>
    <h1>📚 IP Masterlist Dashboard</h1>
  </div>
""", unsafe_allow_html=True)

# Search & Filters
st.markdown("### 🔍 Search Intellectual Property Records")
col1, col2, col3, col4 = st.columns([3,2,2,1])
search_term = col1.text_input("Search by Author or Title")
ip_type = col2.selectbox("Filter by IP Type", ["All"]+sorted(df['IP Type'].unique()))
year_sel = col3.selectbox("Filter by Year", ["All"]+sorted(df['Year'].unique()))
if col4.button("📈 View Summary"):
    st.session_state.show_summary=True; st.experimental_rerun()

with st.expander("📂 Advanced Filters"):
    college = st.selectbox("Filter by College", ["All"]+sorted(df['College'].unique()) if 'College' in df else ["All"])
    campus = st.selectbox("Filter by Campus", ["All"]+sorted(df['Campus'].unique()) if 'Campus' in df else ["All"])
    date_rng = st.date_input("Filter by Date Applied", [])

# Apply Dashboard Filters
df_f = df.copy()
if search_term:
    mask = df_f['Author'].astype(str).str.contains(search_term,case=False)
    if 'Title' in df_f: mask |= df_f['Title'].astype(str).str.contains(search_term,case=False)
    df_f=df_f[mask]
if ip_type!="All": df_f=df_f[df_f['IP Type']==ip_type]
if year_sel!="All": df_f=df_f[df_f['Year']==year_sel]
if college!="All": df_f=df_f[df_f['College']==college]
if campus!="All": df_f=df_f[df_f['Campus']==campus]
if date_rng:
    if len(date_rng)==1: df_f=df_f[df_f['Date Applied']>=pd.to_datetime(date_rng[0])]
    else: df_f=df_f[df_f['Date Applied'].between(pd.to_datetime(date_rng[0]),pd.to_datetime(date_rng[1]))]

# Edit Mode
if st.session_state.role=="Admin" and st.button("✏️ Edit Mode"):
    st.session_state.edit_mode=not st.session_state.edit_mode

if st.session_state.edit_mode:
    st.info("🛠️ Edit Mode: Save or Cancel changes.")
    edited=st.data_editor(df_f, use_container_width=True)
    if st.button("💾 Save Changes"): st.session_state.edited_df=edited; st.success("Saved")
    if st.button("↩️ Cancel"): st.session_state.edit_mode=False; st.experimental_rerun()
else:
    st.dataframe(df_f, use_container_width=True, height=600)
