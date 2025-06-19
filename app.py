import streamlit as st
import pandas as pd
import os
import datetime

# Folder where Excel files are stored
data_folder = "data"

st.set_page_config(page_title="📂 IP Masterlist Dashboard", layout="wide")
st.title("📂 IP Masterlist Dashboard")

# Initialize a container to store the original columns for each IP type
ip_columns = {}

# Load all Excel files from the data folder
@st.cache_data(show_spinner=True)
def load_data():
    df_list = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".xlsx") and filename[:4].isdigit():
            year = filename[:4]
            file_path = os.path.join(data_folder, filename)
            xls = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
            for sheet_name, sheet_df in xls.items():
                sheet_df = sheet_df.copy()
                sheet_df['IP Type'] = sheet_name
                sheet_df['Year'] = year

                # Normalize date columns if they exist
                for col in ['Date Applied', 'Date Approved']:
                    if col in sheet_df.columns:
                        sheet_df[col] = pd.to_datetime(sheet_df[col], errors='coerce')

                # Track original columns per IP type
                if sheet_name not in ip_columns:
                    ip_columns[sheet_name] = sheet_df.columns.tolist()

                df_list.append(sheet_df)

    return pd.concat(df_list, ignore_index=True)

df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Search & Filters")

    # Filter: IP Type
    ip_types = df['IP Type'].dropna().unique().tolist()
    selected_ip = st.selectbox("Filter by IP Type", ["All"] + ip_types)

    # Filter: Search column
    search_column = st.selectbox("Search by", ["Title", "Author"])
    keyword = st.text_input("Search keyword (optional)")

    # Filter: Date Applied
    st.markdown("#### 📅 Filter by Date Applied")
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)

    # Auto-detect categorical filters
    st.markdown("#### 🧠 Advanced Filters")
    cat_cols = df.select_dtypes(include=['object']).nunique()
    categorical_filters = cat_cols[cat_cols.between(2, 100)].index.tolist()

    extra_filters = {}
    for col in categorical_filters:
        if col not in ['Title', 'Author', 'IP Type']:  # skip search columns
            options = df[col].dropna().unique().tolist()
            if len(options) > 1:
                selected = st.multiselect(f"{col}", options)
                if selected:
                    extra_filters[col] = selected

# Apply filters to the DataFrame
filtered_df = df.copy()

if selected_ip != "All":
    filtered_df = filtered_df[filtered_df['IP Type'] == selected_ip]

if keyword:
    filtered_df = filtered_df[filtered_df[search_column].astype(str).str.contains(keyword, case=False, na=False)]

if start_date:
    filtered_df = filtered_df[filtered_df['Date Applied'] >= pd.to_datetime(start_date)]

if end_date:
    filtered_df = filtered_df[filtered_df['Date Applied'] <= pd.to_datetime(end_date)]

for col, selected_values in extra_filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

# Show filtered results (only original columns per IP Type)
st.subheader(f"Showing {len(filtered_df)} records")
if selected_ip != "All":
    display_columns = ip_columns.get(selected_ip, filtered_df.columns.tolist())
    st.dataframe(filtered_df[display_columns])
else:
    st.dataframe(filtered_df)

# Optional: Export
st.download_button("⬇️ Download Filtered Data as CSV", filtered_df.to_csv(index=False).encode('utf-8'), "filtered_data.csv", "text/csv")
