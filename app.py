import datetime

# Set default min/max from your data (with fallback if empty)
min_date = df['Date Applied'].min()
max_date = df['Date Applied'].max()

if pd.isna(min_date):
    min_date = datetime.date(2006, 1, 1)
else:
    min_date = min_date.date()

if pd.isna(max_date):
    max_date = datetime.date(2025, 12, 31)
else:
    max_date = max_date.date()

# Optional Date Filters (you can skip them)
st.sidebar.markdown("### 📅 Filter by Date Applied (Optional)")
start_date = st.sidebar.date_input("Start Date", value=None, min_value=min_date, max_value=max_date, key="start")
end_date = st.sidebar.date_input("End Date", value=None, min_value=min_date, max_value=max_date, key="end")

# 🧼 Filter only if user selected dates
if start_date and not end_date:
    df = df[df['Date Applied'] >= pd.to_datetime(start_date)]
elif end_date and not start_date:
    df = df[df['Date Applied'] <= pd.to_datetime(end_date)]
elif start_date and end_date:
    df = df[(df['Date Applied'] >= pd.to_datetime(start_date)) &
            (df['Date Applied'] <= pd.to_datetime(end_date))]
# else: no filtering applied
