import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="IPRO Masterlist Dashboard", layout="wide")

# --- Logo and Title ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/iprobsu/IPRO/main/ipro_logo.png" alt="IPRO Logo" style="width: 100px; margin-bottom: 10px;" />
        <h1>📚 IP Masterlist Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# --- File Loader ---
def load_data():
    dfs = []
    for year in range(2006, 2026):
        filename = f"{year}.xlsx"
        if os.path.exists(filename):
            xl = pd.ExcelFile(filename)
            for sheet in xl.sheet_names:
                df = xl.parse(sheet)
                df['IP Type'] = sheet
                df['Year'] = year
                dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# Load data
full_df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
authors = sorted(full_df['Author'].dropna().unique()) if 'Author' in full_df else []
ip_types = sorted(full_df['IP Type'].dropna().unique()) if 'IP Type' in full_df else []
dates = pd.to_datetime(full_df['Date Applied'], errors='coerce') if 'Date Applied' in full_df else []

selected_author = st.sidebar.selectbox("Author", ["All"] + authors)
selected_ip = st.sidebar.multiselect("IP Type", ip_types, default=ip_types)

if not dates.empty:
    min_date, max_date = dates.min(), dates.max()
    start_date, end_date = st.sidebar.date_input("Date Range", [min_date, max_date])
else:
    start_date, end_date = None, None

search_term = st.sidebar.text_input("🔎 Search", "")

# --- Filter Logic ---
filtered_df = full_df.copy()

if selected_author != "All":
    filtered_df = filtered_df[filtered_df['Author'] == selected_author]
if selected_ip:
    filtered_df = filtered_df[filtered_df['IP Type'].isin(selected_ip)]
if start_date and end_date and 'Date Applied' in filtered_df.columns:
    filtered_df['Date Applied'] = pd.to_datetime(filtered_df['Date Applied'], errors='coerce')
    filtered_df = filtered_df[(filtered_df['Date Applied'] >= pd.to_datetime(start_date)) &
                              (filtered_df['Date Applied'] <= pd.to_datetime(end_date))]
if search_term:
    search_term = search_term.lower()
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)]

# --- Display Results with Optional Pastel Row Colors ---
if filtered_df.empty:
    st.warning("😕 No records matched your filters or search term.")
else:
    clean_df = filtered_df.dropna(axis=1, how='all')
    clean_df = clean_df.loc[:, ~(clean_df == '').all()]

    st.markdown(f"### 📄 Showing {len(clean_df)} result{'s' if len(clean_df) != 1 else ''}")

    show_colors = st.button("🎨 Customize Row Colors")

    if show_colors and 'IP Type' in clean_df.columns:
        ip_types = sorted(clean_df['IP Type'].dropna().unique())

        pastel_colors = {
            "": "#FFFFFF",
            "🟧 Peach": "#FFD8BE",
            "🟪 Lavender": "#E6CCFF",
            "🟦 Sky Blue": "#AEDFF7",
            "🟩 Mint Green": "#B2F2BB",
            "🟨 Pale Yellow": "#FFFACD",
            "🩷 Soft Pink": "#FFCCE5",
            "🟣 Lilac": "#D0B3FF",
            "🔷 Powder Blue": "#B0E0E6",
            "⬜ Light Gray": "#E8E8E8"
        }

        st.markdown("**Select a pastel color for each IP Type:**")
        selected_colors = {}
        columns = st.columns(len(ip_types))

        for i, ip in enumerate(ip_types):
            with columns[i]:
                choice = st.selectbox(
                    f"{ip}",
                    options=list(pastel_colors.keys()),
                    index=0,
                    key=f"pastel_{ip}"
                )
                selected_colors[ip] = pastel_colors[choice]

        def highlight(row):
            bg = selected_colors.get(row['IP Type'], "#FFFFFF")
            return [f'background-color: {bg}'] * len(row)

        styled_df = clean_df.style.apply(highlight, axis=1)
        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

    else:
        st.dataframe(clean_df, use_container_width=True, height=600)
