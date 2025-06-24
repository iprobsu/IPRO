import streamlit as st
import pandas as pd
import plotly.express as px

# -- Example Stats Section (Integrated into the App) --
st.markdown("## 📊 Dashboard Statistics")
stats_expander = st.expander("📈 View Summary Statistics", expanded=False)

with stats_expander:
    col1, col2 = st.columns(2)

    with col1:
        ip_type_counts = df['IP Type'].value_counts().reset_index()
        ip_type_counts.columns = ['IP Type', 'Count']
        st.markdown("**Total Count by IP Type**")
        fig1 = px.bar(ip_type_counts, x='IP Type', y='Count', color='IP Type', height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        if 'College' in df.columns:
            college_counts = df['College'].value_counts().reset_index()
            college_counts.columns = ['College', 'Count']
            st.markdown("**Total Count by College**")
            fig2 = px.pie(college_counts, names='College', values='Count', height=400)
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        if 'Year' in df.columns:
            year_counts = df['Year'].value_counts().sort_index().reset_index()
            year_counts.columns = ['Year', 'Count']
            st.markdown("**IP Submissions Over the Years**")
            fig3 = px.line(year_counts, x='Year', y='Count', markers=True, height=400)
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        if 'Campus' in df.columns:
            campus_counts = df['Campus'].value_counts().reset_index()
            campus_counts.columns = ['Campus', 'Count']
            st.markdown("**Distribution by Campus**")
            fig4 = px.bar(campus_counts, x='Campus', y='Count', color='Campus', height=400)
            st.plotly_chart(fig4, use_container_width=True)

    # Interactive Filtering (Optional)
    st.markdown("### 🔍 Custom Filtered Stats")
    selected_ip = st.multiselect("Select IP Types to visualize", df['IP Type'].unique())
    selected_college = st.multiselect("Select Colleges", df['College'].unique() if 'College' in df else [])

    custom_df = df.copy()
    if selected_ip:
        custom_df = custom_df[custom_df['IP Type'].isin(selected_ip)]
    if selected_college:
        custom_df = custom_df[custom_df['College'].isin(selected_college)]

    if not custom_df.empty:
        st.markdown("**Filtered IP Count by Year**")
        filtered_stats = custom_df['Year'].value_counts().sort_index().reset_index()
        filtered_stats.columns = ['Year', 'Count']
        fig5 = px.area(filtered_stats, x='Year', y='Count', markers=True, height=300)
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("No matching records for the selected filters.")
