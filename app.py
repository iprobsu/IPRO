from taipy.gui import Gui, notify
import pandas as pd
import os
import altair as alt

# --- Load Data ---
def load_data():
    files = [f for f in os.listdir('data') if f.endswith('.xlsx')]
    records = []
    for f in files:
        yr = f[:4]
        sheets = pd.read_excel(os.path.join('data', f), sheet_name=None, engine='openpyxl')
        for sht, df in sheets.items():
            df['Year'] = yr
            df['IP Type'] = sht
            records.append(df)
    df = pd.concat(records, ignore_index=True)
    df['Date Applied'] = pd.to_datetime(df.get('Date Applied', pd.NaT), errors='coerce')
    df.fillna('', inplace=True)
    if 'Author' in df:
        df['Author'] = df['Author'].astype(str).str.replace(';', ',').str.split(',')
        df['Author'] = df['Author'].apply(lambda L: [x.strip() for x in L])
        df = df.explode('Author').reset_index(drop=True)
    return df

# Global Data
Df = load_data()

# --- GUI Pages ---
index_md = """
<|layout|columns=1 1|gap=20px|>
<|card style='height:100%;'|>
## 📚 IP Masterlist Dashboard

<|Search by Author or Title|input|bind=search_term|style='width:100%'|>
<|Filter by IP Type|selector|lov={ip_types}|bind=ip_type_sel|dropdown|>
<|Filter by Year|selector|lov={years}|bind=year_sel|dropdown|>

<|📈 View Summary|button|on_action=goto_summary|>
<|/card|>
<|card|>
<|Data|table|data=df_display|width=100%|height=400px|>
<|/card|>
<|/layout|>
"""

summary_md = """
<|layout|columns=1|gap=20px|>
<|card|>
## 📊 Summary Statistics
<|← Back to Dashboard|button|on_action=goto_home|style='margin-bottom:10px;'|>
<|layout|columns=1 1 1|>
<|Total Records|metric|value={record_count}|>
<|Distinct IP Types|metric|value={distinct_ip}|>
<|Avg Records/Year|metric|value={avg_per_year:.1f}|>
<|/layout|>
<|/card|>
<|layout|columns=1 1|gap=20px|>
<|card|>
<|bar_data|chart|type=bar|x=IP Type|y=count|title='IP Type Distribution'|height=300px|>
<|/card|>
<|card|>
<|line_data|chart|type=line|x=Year|y=count|title='Submissions Over Time'|height=300px|>
<|/card|>
<|/layout|>
"""

# --- State ---
search_term = ""
ip_type_sel = "All"
year_sel = "All"
ip_types = ["All"] + sorted(Df['IP Type'].unique().tolist())
years = ["All"] + sorted(Df['Year'].unique())
df_display = Df.copy()
bar_data = pd.DataFrame()
line_data = pd.DataFrame()
record_count = 0
distinct_ip = 0
avg_per_year = 0.0

# --- Callbacks ---
def update_filtered(state):
    global df_display
    df_display = Df.copy()
    if state.search_term:
        mask = df_display['Author'].astype(str).str.contains(state.search_term, case=False)
        if 'Title' in df_display:
            mask |= df_display['Title'].astype(str).str.contains(state.search_term, case=False)
        df_display = df_display[mask]
    if state.ip_type_sel != "All":
        df_display = df_display[df_display['IP Type'] == state.ip_type_sel]
    if state.year_sel != "All":
        df_display = df_display[df_display['Year'] == state.year_sel]
    state.df_display = df_display.copy()


def goto_summary(state):
    global bar_data, line_data, record_count, distinct_ip, avg_per_year
    update_filtered(state)
    record_count = len(df_display)
    distinct_ip = df_display['IP Type'].nunique()
    years_count = df_display['Year'].nunique() or 1
    avg_per_year = record_count / years_count
    bar_data = df_display['IP Type'].value_counts().reset_index()
    bar_data.columns = ['IP Type', 'count']
    line_data = df_display['Year'].value_counts().sort_index().reset_index()
    line_data.columns = ['Year', 'count']
    state.page = "summary"


def goto_home(state):
    state.page = "index"

# --- Run GUI ---
Gui(pages={"index": index_md, "summary": summary_md}).run(title="IP Masterlist Dashboard", use_reloader=True)
