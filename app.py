import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# ---------- STYLES ----------
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }
        .glow-logo {
            width: 80px;
            filter: drop-shadow(0 0 8px #00ffaa);
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        h1 {
            text-align: center;
            font-size: 2rem;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- PASSWORDS (Memory Only) ----------
if "passwords" not in st.session_state:
    st.session_state.passwords = {
        "admin": "admin123",
        "mod": "mod123"
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ---------- LOGIN ----------
def login():
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" class="glow-logo" />
            <h1>🔐 Login to Access IP Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if username in st.session_state.passwords and st.session_state.passwords[username] == password:
        st.session_state.logged_in = True
        st.session_state.role = "admin" if username == "admin" else "moderator"
        st.rerun()
    else:
        if username and password:
            st.error("Invalid credentials ❌")

# ---------- LOAD DATA ----------
@st.cache_data
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

# ---------- ADMIN TOOLS ----------
def admin_tools_sidebar():
    st.sidebar.markdown("### 🛠 Admin Tools")
    st.sidebar.subheader("🔁 Replace Existing File")
    file_to_replace = st.sidebar.selectbox("Select file to replace", [f for f in os.listdir("data") if f.endswith(".xlsx")])
    new_file = st.sidebar.file_uploader("Upload new version", type=["xlsx"], key="replace")
    if new_file and st.sidebar.button("Replace File"):
        with open(os.path.join("data", file_to_replace), "wb") as f:
            f.write(new_file.read())
        st.sidebar.success(f"Replaced {file_to_replace}")

    st.sidebar.subheader("➕ Upload New File")
    uploaded_file = st.sidebar.file_uploader("Upload new Excel file", type=["xlsx"], key="upload")
    if uploaded_file and st.sidebar.button("Upload File"):
        save_path = os.path.join("data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.sidebar.success(f"Uploaded {uploaded_file.name}")

    st.sidebar.subheader("🔐 Change Passwords")
    user_to_change = st.sidebar.selectbox("Select user", list(st.session_state.passwords.keys()))
    new_pw = st.sidebar.text_input("New password", type="password")
    if st.sidebar.button("Change Password"):
        st.session_state.passwords[user_to_change] = new_pw
        st.sidebar.success(f"Password updated for {user_to_change}")

# ---------- DASHBOARD ----------
def dashboard():
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" class="glow-logo" />
            <h1>📚 IP Masterlist Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    df = load_data()

    st.markdown("### 🔍 Search Intellectual Property Records")

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search_term = st.text_input("Search by Author or Title")
    with col2:
        ip_type = st.selectbox("Filter by IP Type", ["All"] + sorted(df['IP Type'].unique()))
    with col3:
        year = st.selectbox("Sort by Year", ["All"] + sorted(df['Year'].unique()))

    with st.expander("📂 Advanced Filters"):
        col4, col5, col6 = st.columns(3)
        with col4:
            college = st.selectbox("Filter by College", ["All"] + sorted(df['College'].unique()) if 'College' in df else ["All"])
        with col5:
            campus = st.selectbox("Filter by Campus", ["All"] + sorted(df['Campus'].unique()) if 'Campus' in df else ["All"])
        with col6:
            date_range = st.date_input("Filter by Date Applied", [])

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
    if 'College' in df.columns and college != "All":
        filtered_df = filtered_df[filtered_df['College'] == college]
    if 'Campus' in df.columns and campus != "All":
        filtered_df = filtered_df[filtered_df['Campus'] == campus]
    if date_range:
        if len(date_range) == 1:
            filtered_df = filtered_df[filtered_df['Date Applied'] >= pd.to_datetime(date_range[0])]
        elif len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered_df = filtered_df[filtered_df['Date Applied'].between(start, end)]

    st.sidebar.markdown("🎨 **Customize Row Colors by IP Type**")
    enable_coloring = st.sidebar.checkbox("Enable Row Coloring")

    default_colors = {
        "Copyright": "#FFD8A8",
        "ISBN": "#E6CCFF",
        "ISSN": "#D3D3D3",
        "Industrial Design": "#FFFF99",
        "Trademark": "#ADD8E6",
        "Patent": "#90EE90",
        "Utility Model": "#FFB6C1"
    }

    ip_color_map = default_colors.copy()

    if enable_coloring and 'IP Type' in filtered_df.columns:
        ip_types = sorted(filtered_df['IP Type'].dropna().unique())
        for ip in ip_types:
            default = default_colors.get(ip, "#ffffff")
            ip_color_map[ip] = st.sidebar.color_picker("", default, key=f"color_{ip}")
            st.sidebar.markdown(f"<div style='margin-top:-25px; margin-bottom:10px;'>{ip}</div>", unsafe_allow_html=True)

    if st.session_state.role == "admin":
        st.sidebar.divider()
        admin_tools_sidebar()

    if filtered_df.empty:
        st.warning("😕 No records matched your filters or search term.")
    else:
        display_df = filtered_df.dropna(axis=1, how='all')
        display_df = display_df.loc[:, ~(display_df == '').all()]
        st.markdown(f"### 📄 Showing {len(display_df)} result{'s' if len(display_df) != 1 else ''}")

        if enable_coloring and ip_color_map:
            def apply_color(row):
                bg = ip_color_map.get(row['IP Type'], '#ffffff')
                return [f'background-color: {bg}'] * len(row)
            styled_df = display_df.style.apply(apply_color, axis=1)
            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.dataframe(display_df, use_container_width=True, height=600)

# ---------- MAIN ----------
if not st.session_state.logged_in:
    login()
else:
    dashboard()
