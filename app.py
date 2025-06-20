import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- User Database (Temporary in Memory) ---
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "admin": {"password": "admin123", "role": "Admin"},
        "mod": {"password": "mod123", "role": "Moderator"}
    }

# --- Session State Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Custom Styles ---
st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            margin-top: 10vh;
            padding: 2rem;
            border-radius: 15px;
            background-color: #f5f6f7;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', sans-serif;
        }
        .logo {
            text-align: center;
            margin-bottom: 1rem;
        }
        .logo img {
            width: 80px;
        }
        .logo h2 {
            color: #1877f2;
            margin: 0.5rem 0;
        }
        .footer-text {
            font-size: 0.85rem;
            text-align: center;
            color: #777;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Login/Register Page ---
if not st.session_state.logged_in:
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="logo">'
                    '<img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" />'
                    '<h2>IPRO Dashboard Login</h2>'
                    '</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])

        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                user_db = st.session_state.user_db
                if username in user_db and user_db[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.role = user_db[username]["role"]
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("❌ Invalid username or password")

        with tab2:
            new_user = st.text_input("New Username", key="new_user")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            role = st.selectbox("Select Role", ["Moderator", "Admin"], key="new_role")
            if st.button("Create Account"):
                if new_user in st.session_state.user_db:
                    st.warning("🚫 Username already exists.")
                else:
                    st.session_state.user_db[new_user] = {"password": new_pass, "role": role}
                    st.success("✅ Account created. You can now log in.")

        st.markdown('<div class="footer-text">Not affiliated with Facebook, just vibing.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- Dashboard Code Starts Here ---
st.sidebar.markdown(f"**👤 Logged in as:** `{st.session_state.username}`  ")
st.sidebar.markdown(f"**🔒 Role:** `{st.session_state.role}`")

dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=False)
if dark_mode:
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                background-color: #121212 !important;
                color: #e0e0e0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" style="width: 80px;" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
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

# --- Admin: Upload new data ---
if st.session_state.role == "Admin":
    st.sidebar.markdown("### 📤 Upload New Excel File")
    uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded_file:
        with open(os.path.join("data", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {uploaded_file.name} uploaded. Reload to see updates.")

# --- Filters ---
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

# --- Display Results ---
if filtered_df.empty:
    st.warning("😕 No records matched your filters or search term.")
else:
    display_df = filtered_df.dropna(axis=1, how='all')
    display_df = display_df.loc[:, ~(display_df == '').all()]

    st.markdown(f"### 📄 Showing {len(display_df)} result{'s' if len(display_df) != 1 else ''}")
    st.dataframe(display_df, use_container_width=True, height=600)

    # --- Moderator & Admin: Download filtered data ---
    if st.session_state.role in ["Moderator", "Admin"]:
        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered Results", data=csv, file_name="filtered_ip_data.csv", mime="text/csv")
