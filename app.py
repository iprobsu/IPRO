import streamlit as st
import pandas as pd
import os
import altair as alt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Setup ---
for key, default in {
    "logged_in": False,
    "role": None,
    "edit_mode": False,
    "edited_df": None,
    "dark_mode": False,
    "page": "home"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Navigation Bar ---
st.markdown("""
    <style>
        .nav-container {
            display: flex;
            justify-content: space-around;
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .nav-button {
            background-color: #5f6368;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
        }
        .nav-button:hover {
            background-color: #3c4043;
        }
    </style>
    <div class="nav-container">
        <a href="#" onclick="window.location.reload();" class="nav-button">🏠 Home</a>
        <a href="?page=dashboard" class="nav-button">📚 Dashboard</a>
        <a href="?page=summary" class="nav-button">📊 Summary Statistics</a>
        <a href="?page=admin" class="nav-button">⚙️ Admin Tools</a>
    </div>
""", unsafe_allow_html=True)

if st.query_params.get("page"):
    st.session_state.page = st.query_params["page"]

# --- Dark Mode CSS ---
if st.session_state.dark_mode:
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
            .stButton > button {
                background-color: #5f6368 !important;
                color: #ffffff !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Login Page ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style='max-width: 400px; margin: 100px auto; text-align: center;'>
            <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80' style='margin-bottom: 20px;' />
            <h2>🔐 IPRO Dashboard Login</h2>
        </div>
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

# --- Routing ---
if st.session_state.page == "home":
    st.markdown("""
        <div style='text-align: center;'>
            <img src='https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png' width='80' />
            <h1>🏠 Welcome to the IP Masterlist System</h1>
            <p style='font-size: 18px;'>Use the top navigation to browse sections of the app.</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "dashboard":
    st.markdown("## 📚 IP Dashboard")
    st.write("(Coming soon: full dashboard logic)")

elif st.session_state.page == "summary":
    st.markdown("## 📈 Summary Statistics Panel")
    filtered_df = df.copy()

    st.markdown("### 🎯 KPIs")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="Total Entries", value=len(filtered_df))
    with kpi2:
        most_common = filtered_df['IP Type'].mode()[0] if not filtered_df.empty else "N/A"
        st.metric(label="Most Common IP Type", value=most_common)
    with kpi3:
        top_author = filtered_df['Author'].value_counts().idxmax() if 'Author' in filtered_df else "N/A"
        st.metric(label="Top Author", value=top_author)

    if 'IP Type' in filtered_df:
        st.altair_chart(alt.Chart(filtered_df).mark_bar().encode(
            x='IP Type', y='count()', color='IP Type', tooltip=['IP Type', 'count()']
        ).properties(title="IP Type Distribution"), use_container_width=True)

    if 'College' in filtered_df:
        st.altair_chart(alt.Chart(filtered_df).mark_arc().encode(
            theta='count()', color='College', tooltip=['College', 'count()']
        ).properties(title="Distribution by College"), use_container_width=True)

    if 'Year' in filtered_df:
        year_df = filtered_df['Year'].value_counts().reset_index()
        year_df.columns = ['Year', 'Count']
        st.altair_chart(alt.Chart(year_df).mark_line(point=True).encode(
            x='Year', y='Count', tooltip=['Year', 'Count']
        ).properties(title="IP Submissions Over Time"), use_container_width=True)

elif st.session_state.page == "admin" and st.session_state.role == "Admin":
    st.markdown("## ⚙️ Admin Tools")
    st.write("(Coming soon: admin-only features for managing data, users, etc.)")

elif st.session_state.page == "admin":
    st.warning("🔒 Access denied. Admins only.")
