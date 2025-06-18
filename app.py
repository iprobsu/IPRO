import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📚 IP Masterlist Dashboard", layout="wide")
st.title("📂 Intellectual Property Dashboard")

uploaded_files = st.file_uploader("📤 Upload Excel files (2006–2025)", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    df_list = []
    for file in uploaded_files:
        sheets = pd.read_excel(file, sheet_name=None, engine="openpyxl")
        for sheet_name, data in sheets.items():
            data["IP Type"] = sheet_name
            df_list.append(data)

    df = pd.concat(df_list, ignore_index=True)
    df.fillna('', inplace=True)

    # Fix date columns if they exist
    for col in ['Date Applied', 'Date Approved']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Normalize Author column
    if 'Author' in df.columns:
        df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
        df['Author'] = df['Author'].apply(lambda x: [a.strip() for a in x])
        df = df.explode('Author').reset_index(drop=True)

    # Sidebar filters
    with st.sidebar:
        st.header("🔎 Filter Data")
        authors = st.multiselect("Filter by Author", options=sorted(df['Author'].unique()), default=None)
        ip_types = st.multiselect("Filter by IP Type", options=sorted(df['IP Type'].unique()), default=None)
        years = st.multiselect("Filter by Year (Date Applied)", options=sorted(df['Date Applied'].dt.year.dropna().unique()), default=None)

    filtered_df = df.copy()

    if authors:
        filtered_df = filtered_df[filtered_df['Author'].isin(authors)]

    if ip_types:
        filtered_df = filtered_df[filtered_df['IP Type'].isin(ip_types)]

    if years and 'Date Applied' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Date Applied'].dt.year.isin(years)]

    st.success(f"🎯 Showing {len(filtered_df)} results")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered Data", csv, "filtered_ip_data.csv", "text/csv")

else:
    st.warning("📎 Please upload Excel files to begin.")
