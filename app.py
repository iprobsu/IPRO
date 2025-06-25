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

# --- Sidebar Navigation ---
st.sidebar.title("IPRO Cloud")
nav_items = {
    "home": "🏠 Home",
    "edit": "✏️ Edit Data",
    "summary": "📊 Summary"
}
for key, label in nav_items.items():
    if st.sidebar.button(label):
        st.session_state.page = key

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.session_state.page = 'login'
    st.experimental_rerun()

# --- Dark Mode Toggle ---
dark_mode_toggle_color = "#e8eaed" if not st.session_state.dark_mode else "#ffffff"
st.sidebar.markdown(f"<span style='color: {dark_mode_toggle_color}'>🔒 Current Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=st.session_state.dark_mode)
dark_mode = st.session_state.dark_mode

# --- Dark Mode Styling ---
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

# --- Load Data ---
def load_data():
    files = [f for f in os.listdir("data") if f.endswith(".xlsx")]
    records = []
    for f in files:
        year = f[:4]
        xls = pd.read_excel(os.path.join("data", f), sheet_name=None, engine="openpyxl")
        for sht, df in xls.items():
            df['Year'] = year; df['IP Type'] = sht
            records.append(df)
    df = pd.concat(records, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df:
        df['Author'] = df['Author'].astype(str).str.replace(';',',').str.split(',')
        df['Author'] = df['Author'].apply(lambda L: [x.strip() for x in L])
        df = df.explode('Author').reset_index(drop=True)
    return df

if st.session_state.logged_in:
    df = load_data()

# --- Page Views ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.markdown("# 🏠 IP Masterlist Dashboard")
    search_term = st.text_input("🔍 Search by Author or Title", value="")
    ip_type = st.selectbox("Filter by IP Type", ['All'] + sorted(df['IP Type'].dropna().unique().tolist()))
    year = st.selectbox("Filter by Year", ['All'] + sorted(df['Year'].dropna().unique().tolist()))
    with st.expander("⚙️ Advanced Filters"):
        college = st.selectbox("Filter by College", ['All'] + sorted(df['College'].dropna().astype(str).unique().tolist()) if 'College' in df.columns else ['All'])
        campus = st.selectbox("Filter by Campus", ['All'] + sorted(df['Campus'].dropna().astype(str).unique().tolist()) if 'Campus' in df.columns else ['All'])
        date_range = st.date_input("Filter by Date Applied", [])

    dff = df.copy()
    if search_term:
        mask = dff['Author'].astype(str).str.contains(search_term, case=False)
        mask |= dff['Title'].astype(str).str.contains(search_term, case=False)
        dff = dff[mask]
    if ip_type != 'All': dff = dff[dff['IP Type']==ip_type]
    if year!='All': dff = dff[dff['Year']==year]
    if 'College' in dff.columns and college!='All': dff = dff[dff['College']==college]
    if 'Campus' in dff.columns and campus!='All': dff = dff[dff['Campus']==campus]
    if date_range:
        if len(date_range)==1: dff = dff[dff['Date Applied']>=pd.to_datetime(date_range[0])]
        elif len(date_range)==2: dff = dff[dff['Date Applied'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))]

    st.dataframe(dff, use_container_width=True, height=600)

elif st.session_state.page == "edit":
    st.markdown("# ✏️ Edit Data")
    st.write("Search, add, or delete entries below.")
    selected_year = st.selectbox("Select Year (file)", sorted(df['Year'].unique()))
    sub_df = df[df['Year']==selected_year].copy()
    sub_df['Delete'] = False
    edited = st.data_editor(sub_df, use_container_width=True)
    st.markdown("**Actions:**")
    if st.button("Save Changes"):
        st.session_state.edited_df = edited
        st.success("Changes saved in session.")
    if st.button("Apply Deletions"):
        to_delete = edited[edited['Delete']]
        st.write(f"Deleting {len(to_delete)} rows...")
        st.success("Deletion logic placeholder")

elif st.session_state.page == "summary":
    st.markdown("# 📊 Summary Statistics")
    total = len(df)
    distinct = df['IP Type'].nunique()
    years = df['Year'].nunique()
    avg = total/years if years else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records", total)
    c2.metric("Distinct IP Types", distinct)
    c3.metric("Avg Records/Year", f"{avg:.1f}")
    st.altair_chart(alt.Chart(df).mark_bar().encode(x='IP Type', y='count()', color='IP Type'), use_container_width=True)
    year_df = df['Year'].value_counts().reset_index(); year_df.columns=['Year','Count']
    st.altair_chart(alt.Chart(year_df).mark_line(point=True).encode(x='Year', y='Count'), use_container_width=True)
    if st.button("← Back to Dashboard"):
        st.session_state.page='home'
        st.experimental_rerun()
