import streamlit as st
import pandas as pd
import os

# --- Streamlit Page Settings ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Roboto Font, Logo Styling, and Bounce Animation ---
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
        <img src="https://raw.githubusercontent.com/iprobsu/ip-dashboard/main/ipro-logo.png" alt="IPRO Logo" class="glow-logo" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# --- Load All Excel Data ---
@st.cache_data
def load_data():
    data_dir = "data"
    all_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".xlsx"):
            year = filename[:4]
            file_path = os.path.join(data_dir, filename)
            xls = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
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

# --- Filter UI ---
st.markdown("### 🔍 Search Intellectual Property Records")

col1, col2, col3 = st.columns([3, 2, 2])

with col1:
    search_term = st.text_input("Search by Author or Title")

with col2:
    ip_type = st.selectbox("Filter by IP Type", ["All"] + sorted(df['IP Type'].unique()))

with col3:
    year_filter = st.selectbox("Sort by Year", ["All"] + sorted(df['Year'].unique()))

# --- Advanced Filters ---
with st.expander("📂 Advanced Filters"):
    col4, col5, col6 = st.columns(3)
    with col4:
        college = st.selectbox("Filter by College", ["All"] + sorted(df['College'].unique()) if 'College' in df else ["All"])
    with col5:
        campus = st.selectbox("Filter by Campus", ["All"] + sorted(df['Campus'].unique()) if 'Campus' in df else ["All"])
    with col6:
        date_range = st.date_input("Filter by Date Applied (optional)", [])

# --- Apply Filters ---
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df['Author'].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df['Title'].astype(str).str.contains(search_term, case=False, na=False)
    ]

if ip_type != "All":
    filtered_df = filtered_df[filtered_df['IP Type'] == ip_type]

if year_filter != "All":
    filtered_df = filtered_df[filtered_df['Year'] == year_filter]

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

# --- Display Results with Dynamic Columns and Coloring ---
if filtered_df.empty:
    st.warning("😕 No records matched your filters or search term.")
else:
    # Remove columns that are all blank
    non_empty_df = filtered_df.dropna(axis=1, how='all')
    non_empty_df = non_empty_df.loc[:, ~(non_empty_df == '').all()]

    # Sidebar color picker toggle
    st.sidebar.markdown("🎨 Customize Row Colors by IP Type")
    enable_coloring = st.sidebar.checkbox("Enable IP Type Coloring")

    color_map = {}
    unique_types = sorted(non_empty_df['IP Type'].dropna().unique())

    if enable_coloring:
        for ip_type in unique_types:
            default = "#ffffff"  # default background color
            picked_color = st.sidebar.color_picker(f"{ip_type} color", value=default)
            color_map[ip_type] = picked_color

        def style_rows(row):
            color = color_map.get(row['IP Type'], '#ffffff')
            return [f'background-color: {color}'] * len(row)

        styled_df = non_empty_df.style.apply(style_rows, axis=1)
        st.markdown(f"### 📄 Showing {len(non_empty_df)} results")
        st.write(styled_df)
    else:
        st.markdown(f"### 📄 Showing {len(non_empty_df)} results")
        st.dataframe(non_empty_df, use_container_width=True, height=600)
