import streamlit as st
import pandas as pd
import os
import altair as alt

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- 💖 Sidebar Toggle Hack ---
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none;
        }
        #custom-sidebar-toggle {
            position: fixed;
            top: 20px;
            left: 15px;
            z-index: 999;
            background-color: #ff66b2;
            color: white;
            padding: 8px 12px;
            border-radius: 50%;
            font-size: 22px;
            cursor: pointer;
            box-shadow: 0 0 12px #ff66b2;
        }
        #custom-sidebar-toggle:hover {
            background-color: #ff3399;
        }
    </style>
    <script>
        function toggleSidebar() {
            const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
            if (sidebar.style.transform === 'translateX(-100%)') {
                sidebar.style.transform = 'translateX(0%)';
            } else {
                sidebar.style.transform = 'translateX(-100%)';
            }
        }
    </script>
    <div id="custom-sidebar-toggle" onclick="toggleSidebar()">💖</div>
""", unsafe_allow_html=True)

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

# --- Dark Mode Styling ---
dark_mode_toggle_color = "#e8eaed" if not st.session_state.dark_mode else "#ffffff"
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            html, body {
                background-color: #202124 !important;
                color: #e8eaed !important;
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
            .st-bb, .st-bc, .stMarkdown, .stText, .stTextInput, .stSelectbox, .stDateInput, .stMultiSelect {
                color: #e8eaed !important;
            }
            .stDataFrameContainer, .stDataEditorContainer {
                background-color: #202124 !important;
                color: #e8eaed !important;
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
        <div style="max-width: 400px; margin: 100px auto; padding: 20px; text-align: center;">
            <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" width="80"
                 style="filter: drop-shadow(0 0 10px #00ffaa); animation: bounce 2s infinite;" />
            <h2>🔐 IPRO Dashboard Login</h2>
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

# --- Sidebar Navigation ---
st.sidebar.image("https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png", width=80)
st.sidebar.markdown("<h2 style='text-align: center;'>📚 IPRO Cloud</h2>", unsafe_allow_html=True)

st.sidebar.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            min-width: 250px !important;
            width: 250px !important;
        }
        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

nav_items = {
    "home": "🏠 Home",
    "edit": "✏️ Edit Data",
    "summary": "📊 Summary"
}

if "page" not in st.session_state:
    st.session_state.page = "home"

for key, label in nav_items.items():
    if st.sidebar.button(label):
        st.session_state.page = key

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.experimental_rerun()

st.sidebar.markdown(f"<span style='color: {dark_mode_toggle_color}'>🔒 Current Role: {st.session_state.role}</span>", unsafe_allow_html=True)
st.session_state.dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=st.session_state.dark_mode)

# --- Load Data ---
def load_data():
    files = [f for f in os.listdir("data") if f.endswith(".xlsx")]
    records = []
    for f in files:
        year = f[:4]
        xls = pd.read_excel(os.path.join("data", f), sheet_name=None, engine="openpyxl")
        for sht, df in xls.items():
            df['Year'] = year
            df['IP Type'] = sht
            records.append(df)
    df = pd.concat(records, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df:
        df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
        df['Author'] = df['Author'].apply(lambda x: [a.strip() for a in x])
        df = df.explode('Author').reset_index(drop=True)
    return df

df = load_data()

# --- Logo & Title ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" width="80"
             style="filter: drop-shadow(0 0 10px #00ffaa); animation: bounce 2s infinite;" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    </style>
""", unsafe_allow_html=True)

# --- PAGE ROUTING ---
if st.session_state.page == "home":
    st.subheader("🏠 Home")
    st.markdown("""
    Welcome to the **IP Masterlist Dashboard**.  
    Use the sidebar to:
    - ✏️ Edit existing IP records
    - 📊 View statistics
    - 🔐 Manage admin and moderator access
    """)

elif st.session_state.page == "edit":
    st.subheader("✏️ Edit Data")
    if st.session_state.role == "Admin":
        st.markdown("You can edit the table below:")
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        st.session_state.edited_df = edited_df
        if st.button("💾 Save Changes (not functional yet)"):
            st.warning("Saving is not implemented yet.")
    else:
        st.warning("You must be an Admin to edit data.")

elif st.session_state.page == "summary":
    st.subheader("📊 Summary")
    summary = df.groupby("IP Type").size().reset_index(name="Count")

    chart = alt.Chart(summary).mark_bar().encode(
        x=alt.X('IP Type:N', title="IP Type"),
        y=alt.Y('Count:Q', title="Number of Records"),
        tooltip=['IP Type', 'Count']
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)
