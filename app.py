import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="📂 IP Masterlist Dashboard", layout="wide")

st.title("📂 IP Masterlist Dashboard")
st.caption("Automatically loads Excel files from 2006–2025 with multiple sheets per IP Type")

# --- Load all Excel files in the 'data' folder ---
data_folder = "data"
excel_files = [f for f in os.listdir(data_folder) if f.endswith(".xlsx")]

if not excel_files:
    st.warning("No Excel files found in the 'data' folder. Please upload some.")
    st.stop()

# --- Read all Excel files and all sheets into one DataFrame ---
df_list = []
for file in excel_files:
    file_path = os.path.join(data_folder, file)
    xls = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
    for sheet_name, sheet_df in xls.items():
        sheet_df = sheet_df.copy()
        sheet_df['IP Type'] = sheet_name  # Track which sheet this came from
        sheet_df['Source File'] = file    # Track which file this came from
        df_list.append(sheet_df)

# Combine all, keeping all columns
master_df = pd.concat(df_list, ignore_index=True, sort=False)

# Normalize Author column if it exists
if 'Author' in master_df.columns:
    master_df['Author'] = master_df['Author'].astype(str).str.replace(';', ',', regex=False)
    master_df['Author'] = master_df['Author'].str.split(',').apply(lambda x: [a.strip() for a in x])
    master_df = master_df.explode('Author').reset_index(drop=True)

# Try to coerce date columns
for col in ['Date Applied', 'Date Approved']:
    if col in master_df.columns:
        master_df[col] = pd.to_datetime(master_df[col], errors='coerce')

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# IP Type Filter
ip_types = master_df['IP Type'].dropna().unique()
selected_ip_types = st.sidebar.multiselect("Filter by IP Type", ip_types, default=list(ip_types))
filtered_df = master_df[master_df['IP Type'].isin(selected_ip_types)]

# Author Filter
if 'Author' in filtered_df.columns:
    all_authors = filtered_df['Author'].dropna().unique()
    selected_authors = st.sidebar.multiselect("Filter by Author", all_authors)
    if selected_authors:
        filtered_df = filtered_df[filtered_df['Author'].isin(selected_authors)]

# Date Range Filter
if 'Date Applied' in filtered_df.columns:
    min_date = filtered_df['Date Applied'].min()
    max_date = filtered_df['Date Applied'].max()
    start_date, end_date = st.sidebar.date_input("Date Applied Range", [min_date, max_date])
    filtered_df = filtered_df[(filtered_df['Date Applied'] >= pd.to_datetime(start_date)) &
                              (filtered_df['Date Applied'] <= pd.to_datetime(end_date))]

# --- Display ---
st.markdown(f"### Showing {len(filtered_df):,} records")
st.dataframe(filtered_df, use_container_width=True)

# --- Optional: Download Button ---
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name=f"filtered_ip_data_{datetime.today().date()}.csv",
    mime='text/csv'
)

st.caption("👩‍💻 Built with 💙 by Krisha's AI sidekick. All rights reserved, IP included.")
