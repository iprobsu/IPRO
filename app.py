import streamlit as st
import pandas as pd
import os
import altair as alt

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Defaults ---
def init_state():
    defaults = {
        'page': 'home',
        'logged_in': False,
        'role': None,
        'edit_mode': False,
        'edited_df': None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --- Authentication (Login) ---
if not st.session_state.logged_in:
    st.title("🔐 IPRO Dashboard Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = 'Admin'
            st.session_state.page = 'home'
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
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

# Load once
if st.session_state.logged_in:
    df = load_data()

# --- Sidebar Navigation (Huawei Cloud style) ---
st.sidebar.title("IPRO Cloud")
nav_items = {
    'home': '🏠 Home',
    'edit': '✏️ Edit Data',
    'summary': '📊 Summary'
}
for key, label in nav_items.items():
    if st.sidebar.button(label):
        st.session_state.page = key

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.session_state.page = 'login'
    st.experimental_rerun()

# --- Main Content ---
if st.session_state.page == 'home':
    # Home / Dashboard view
    st.markdown("# 🏠 IP Masterlist Dashboard")
    search_term = st.text_input("🔍 Search by Author or Title", value="")
    ip_type = st.selectbox("Filter by IP Type", ['All'] + sorted(df['IP Type'].unique()))
    year = st.selectbox("Filter by Year", ['All'] + sorted(df['Year'].unique()))
    with st.expander("⚙️ Advanced Filters"):
        college = st.selectbox("Filter by College", ['All'] + sorted(df.get('College', []).astype(str).unique()))
        campus = st.selectbox("Filter by Campus", ['All'] + sorted(df.get('Campus', []).astype(str).unique()))
        date_range = st.date_input("Filter by Date Applied", [])
    # Apply filters
    dff = df.copy()
    if search_term:
        mask = dff['Author'].astype(str).str.contains(search_term, case=False)
        mask |= dff['Title'].astype(str).str.contains(search_term, case=False)
        dff = dff[mask]
    if ip_type != 'All': dff = dff[dff['IP Type']==ip_type]
    if year!='All': dff = dff[dff['Year']==year]
    if 'College' in dff and college!='All': dff = dff[dff['College']==college]
    if 'Campus' in dff and campus!='All': dff = dff[dff['Campus']==campus]
    if date_range:
        if len(date_range)==1: dff = dff[dff['Date Applied']>=pd.to_datetime(date_range[0])]
        else: dff = dff[dff['Date Applied'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))]
    st.dataframe(dff, use_container_width=True, height=600)

elif st.session_state.page == 'edit':
    # Edit Data view
    st.markdown("# ✏️ Edit Data")
    st.write("Search, add, or delete entries below.")
    # simple file selector by year
    selected_year = st.selectbox("Select Year (file)", sorted(df['Year'].unique()))
    sub_df = df[df['Year']==selected_year]
    # Data editor with delete: add a 'Delete' column of checkboxes
    sub_df['Delete'] = False
    edited = st.data_editor(sub_df, use_container_width=True)
    st.markdown("**Actions:**")
    if st.button("Save Changes"):
        st.session_state.edited_df = edited
        st.success("Changes saved in session.")
    if st.button("Apply Deletions"):
        to_delete = edited[edited['Delete']]
        st.write(f"Deleting {len(to_delete)} rows...")
        # implement deletion logic here
        notify = st.success("Deletion logic placeholder")

elif st.session_state.page == 'summary':
    # Summary Statistics view
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
