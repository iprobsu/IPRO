import streamlit as st
import pandas as pd
import os

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Dark Mode Toggle ---
st.sidebar.markdown("### ⚙️ Appearance Settings")
dark_mode = st.sidebar.toggle("🌗 Enable Dark Mode", value=False)

# --- Apply Dark Mode Styling ---
if dark_mode:
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                background-color: #121212 !important;
                color: #e0e0e0 !important;
                font-family: 'Roboto', sans-serif;
            }

            .stTextInput input, .stSelectbox div, .stDateInput input, .stMultiSelect div {
                background-color: #2c2c2c !important;
                color: #ffffff !important;
                border: none !important;
            }

            .stDataFrame, .stTable {
                background-color: #1e1e1e !important;
                color: #ffffff !important;
            }

            .block-container, .sidebar-content, .css-1avcm0n, .css-1d391kg {
                background-color: #121212 !important;
                color: #ffffff !important;
            }

            h1, h2, h3, h4, h5, h6 {
                color: #ffffff !important;
            }

            .stButton>button {
                background-color: #333333 !important;
                color: #ffffff !important;
                border: none !important;
            }

            .glow-logo {
                filter: drop-shadow(0 0 10px #00ffaa);
            }
        </style>
    """, unsafe_allow_html=True)

# --- Fonts & Logo Styling ---
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

# --- Logo and Title ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" class="glow-logo" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# --- Load All Excel Files ---
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

df = load_data()

# --- Filters ---
st.markdown("### 🔍 Search Intellectual Property Records")

col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    search_term = st.text_input("Search by Author or Title")
with col2:
    ip_type = st.selectbox("Filter by IP Type", ["All"] + sorted(df['IP Type'].unique()))
with col3:
    year = st.selectbox("Sort by Year", ["All"] + sorted(df['Year'].unique()))

# --- Advanced Filters ---
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

# --- Sidebar: Row Highlight Colors ---
st.sidebar.markdown("### 🎛️ Row Colors by IP Type")
show_colors = st.sidebar.toggle("🎨 Customize Row Colors", value=False)

ip_color_map = {}
enable_coloring = False

if show_colors:
    enable_coloring = st.sidebar.checkbox("Enable Row Coloring", value=True)
    
    if 'IP Type' in filtered_df.columns:
        ip_types = sorted(filtered_df['IP Type'].dropna().unique())
        for ip in ip_types:
            col1, col2 = st.sidebar.columns([1, 4])
            with col1:
                ip_color_map[ip] = st.color_picker("", "#ffffff", key=f"color_{ip}")
            with col2:
                st.sidebar.markdown(f"<div style='margin-top: 8px'>{ip}</div>", unsafe_allow_html=True)

# --- Display Results ---
if filtered_df.empty:
    st.warning("😕 No records matched your filters or search term.")
else:
    display_df = filtered_df.dropna(axis=1, how='all')
    display_df = display_df.loc[:, ~(display_df == '').all()]

    st.markdown(f"### 📄 Showing {len(display_df)} result{'s' if len(display_df) != 1 else ''}")

    if enable_coloring and ip_color_map:
        def apply_color(row):
            bg = ip_color_map.get(row['IP Type'], '#ffffff')
            text_color = '#ffffff' if dark_mode else '#000000'
            return [f'background-color: {bg}; color: {text_color}'] * len(row)

        styled_df = display_df.style.apply(apply_color, axis=1)
        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.dataframe(display_df, use_container_width=True, height=600)
