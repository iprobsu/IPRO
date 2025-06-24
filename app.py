import streamlit as st
import pandas as pd
import os
import altair as alt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Setup ---
defaults = {
    "logged_in": False,
    "role": None,
    "edit_mode": False,
    "edited_df": None,
    "dark_mode": False,
    "page": "dashboard"
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Sidebar: Role & Dark Mode ---
role_color = "#e8eaed" if st.session_state.dark_mode else "#202124"
st.sidebar.markdown(f"<span style='color: {role_color}; font-weight:bold;'>🔒 Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Dark Mode", value=st.session_state.dark_mode)

# --- Navigation ---
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Dashboard"):
    st.session_state.page = "dashboard"
elif st.sidebar.button("📊 Summary Stats"):
    st.session_state.page = "summary"

# --- Dark Mode CSS ---
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        html, body, [class*="main"] {background-color: #202124 !important; color: #e8eaed !important;}
        [data-testid="stSidebar"], .block-container {background-color: #202124 !important;}
        input, select, textarea {background-color: #303134 !important; color: #e8eaed !important;}
        .stButton > button {background-color: #5f6368 !important; color: #ffffff !important;}
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
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u=="admin" and p=="admin123":
                st.session_state.logged_in=True; st.session_state.role="Admin"; st.experimental_rerun()
            elif u=="mod" and p=="mod123":
                st.session_state.logged_in=True; st.session_state.role="Moderator"; st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# --- Load Data Function ---
def load_data():
    files = [f for f in os.listdir("data") if f.endswith('.xlsx')]
    dfs=[]
    for f in files:
        year=f[:4]
        xls=pd.read_excel(os.path.join('data',f), sheet_name=None, engine='openpyxl')
        for sheet,df in xls.items():
            df['Year']=year; df['IP Type']=sheet
            dfs.append(df)
    df=pd.concat(dfs,ignore_index=True)
    df['Date Applied']=pd.to_datetime(df.get('Date Applied',pd.NaT),errors='coerce')
    df.fillna('',inplace=True)
    if 'Author' in df:
        df['Author']=df['Author'].astype(str).str.replace(';',',').str.split(',')
        df['Author']=df['Author'].apply(lambda lst:[x.strip() for x in lst])
        df=df.explode('Author').reset_index(drop=True)
    return df

df=load_data()

# --- Page: Summary ---
if st.session_state.page=='summary':
    st.markdown("## 📊 Summary Statistics")
    if st.button("← Back to Dashboard"):
        st.session_state.page='dashboard'; st.experimental_rerun()
    st.metric("Total Records", len(df))
    st.metric("Distinct IP Types", df['IP Type'].nunique())
    if 'IP Type' in df:
        chart=alt.Chart(df).mark_bar().encode(x='IP Type',y='count()').properties(title='IP Type Distribution')
        st.altair_chart(chart,use_container_width=True)
    if 'Year' in df:
        year_counts=df['Year'].value_counts().reset_index(); year_counts.columns=['Year','Count']
        line=alt.Chart(year_counts).mark_line(point=True).encode(x='Year',y='Count').properties(title='Submissions Over Time')
        st.altair_chart(line,use_container_width=True)
    st.stop()

# --- Page: Dashboard ---
if st.session_state.page == 'dashboard':
    # Logo & Title
    st.markdown("""
    <div style='text-align:center;'>
      <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80'/>
      <h1>📚 IP Masterlist Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

    # Search & Filter UI
    st.markdown("### 🔍 Search Records")
    col1, col2, col3 = st.columns([3, 2, 2])
    search_term = col1.text_input("Search by Author or Title")
    ip_type = col2.selectbox("Filter by IP Type", ["All"] + sorted(df['IP Type'].unique()))
    year_sel = col3.selectbox("Filter by Year", ["All"] + sorted(df['Year'].unique()))
    with st.expander("Advanced Filters"):
        college_sel = st.selectbox(
            "Filter by College", ["All"] + sorted(df['College'].unique()) if 'College' in df else ["All"]
        )
        campus_sel = st.selectbox(
            "Filter by Campus", ["All"] + sorted(df['Campus'].unique()) if 'Campus' in df else ["All"]
        )
        date_range = st.date_input("Filter by Date Applied", [])

    # Apply Filters
    df_f = df.copy()
    if search_term:
        mask = df_f['Author'].astype(str).str.contains(search_term, case=False, na=False)
        if 'Title' in df_f.columns:
            mask |= df_f['Title'].astype(str).str.contains(search_term, case=False, na=False)
        df_f = df_f[mask]
    if ip_type != "All":
        df_f = df_f[df_f['IP Type'] == ip_type]
    if year_sel != "All":
        df_f = df_f[df_f['Year'] == year_sel]
    if 'College' in df and college_sel != "All":
        df_f = df_f[df_f['College'] == college_sel]
    if 'Campus' in df and campus_sel != "All":
        df_f = df_f[df_f['Campus'] == campus_sel]
    if date_range:
        if len(date_range) == 1:
            df_f = df_f[df_f['Date Applied'] >= pd.to_datetime(date_range[0])]
        elif len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df_f = df_f[df_f['Date Applied'].between(start, end)]

    # Editable Table View
    if st.session_state.role == "Admin":
        if st.button("✏️ Edit Mode"):
            st.session_state.edit_mode = not st.session_state.edit_mode

    if st.session_state.edit_mode:
        st.info("🛠️ Edit Mode enabled. Save or Cancel your changes.")
        edited = st.data_editor(df_f, use_container_width=True)
        col_save, col_cancel = st.columns([1,1])
        with col_save:
            if st.button("💾 Save Changes"):
                st.session_state.edited_df = edited
                st.success("✅ Changes saved in session.")
        with col_cancel:
            if st.button("↩️ Cancel"):
                st.session_state.edit_mode = False
                st.experimental_rerun()
    else:
        st.dataframe(df_f, use_container_width=True, height=600)
