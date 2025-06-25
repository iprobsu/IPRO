import streamlit as st
import pandas as pd
import os
import altair as alt

# --- Page Setup ---
st.set_page_config(page_title="IP Masterlist Dashboard", layout="wide")

# --- Session State Setup ---
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Assume always logged in for this example

# --- Load Data ---
def load_data():
    files = [f for f in os.listdir("data") if f.endswith(".xlsx")]
    all_data = []
    for file in files:
        year = file[:4]
        xls = pd.read_excel(os.path.join("data", file), sheet_name=None, engine="openpyxl")
        for sheet_name, df in xls.items():
            df["Year"] = year
            df["IP Type"] = sheet_name
            all_data.append(df)
    df = pd.concat(all_data, ignore_index=True)
    df["Date Applied"] = pd.to_datetime(df.get("Date Applied", pd.NaT), errors="coerce")
    df["Date Approved"] = pd.to_datetime(df.get("Date Approved", pd.NaT), errors="coerce")
    df.fillna("", inplace=True)
    if "Author" in df.columns:
        df["Author"] = df["Author"].astype(str).str.replace(";", ",").str.split(",")
        df["Author"] = df["Author"].apply(lambda x: [a.strip() for a in x])
        df = df.explode("Author").reset_index(drop=True)
    return df

df = load_data()

# --- Navigation Bar ---
with st.container():
    st.markdown("""
    <style>
    .nav-bar {
        background-color: #1f2937;
        padding: 10px 0;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    .nav-bar button {
        margin: 0 10px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        background-color: #374151;
        color: #ffffff;
    }
    .nav-bar button:hover {
        background-color: #4b5563;
    }
    </style>
    <div class="nav-bar">
        <form method="post">
            <button onclick="window.location.reload(); return false;">🏠 Home</button>
            <button onclick="window.location.href='?page=summary'; return false;">📊 Summary Statistics</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

    # Simulate navigation
    page = st.query_params.get("page", "dashboard")
    st.session_state.page = page

# --- Dashboard Page ---
if st.session_state.page == "dashboard":
    st.title("📚 IP Masterlist Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("Search by Author or Title")
    with col2:
        ip_type = st.selectbox("Filter by IP Type", ["All"] + sorted(df["IP Type"].unique()))
    with col3:
        year = st.selectbox("Sort by Year", ["All"] + sorted(df["Year"].unique()))

    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df["Author"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["Title"].astype(str).str.contains(search_term, case=False, na=False)
        ]
    if ip_type != "All":
        filtered_df = filtered_df[filtered_df["IP Type"] == ip_type]
    if year != "All":
        filtered_df = filtered_df[filtered_df["Year"] == year]

    st.dataframe(filtered_df, use_container_width=True)

# --- Summary Statistics Page ---
elif st.session_state.page == "summary":
    st.title("📊 Summary Statistics")
    st.markdown("<style>h1{ text-align: center; }</style>", unsafe_allow_html=True)

    total = len(df)
    distinct_types = df['IP Type'].nunique()
    years_count = df['Year'].nunique()
    avg_year = total / years_count if years_count else 0

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="Total Records", value=total)
    with kpi2:
        st.metric(label="Distinct IP Types", value=distinct_types)
    with kpi3:
        st.metric(label="Avg Records per Year", value=f"{avg_year:.2f}")

    bar = alt.Chart(df).mark_bar().encode(
        x='IP Type', y='count()', color='IP Type', tooltip=['IP Type', 'count()']
    ).properties(title="IP Type Distribution")
    st.altair_chart(bar, use_container_width=True)

    line_data = df['Year'].value_counts().reset_index()
    line_data.columns = ['Year', 'Count']
    line_chart = alt.Chart(line_data).mark_line(point=True).encode(
        x='Year', y='Count', tooltip=['Year', 'Count']
    ).properties(title="IP Submissions Over Time")
    st.altair_chart(line_chart, use_container_width=True)

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.experimental_rerun()
