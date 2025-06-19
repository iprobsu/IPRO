# --- Sidebar: Row Highlight Colors ---
with st.sidebar:
    st.markdown("### 🎛️ Options")
    show_colors = st.toggle("🎨 Customize Row Colors", value=False)

if show_colors:
    st.sidebar.markdown("---")
    st.sidebar.markdown("🎨 **Customize Row Colors by IP Type**")
    enable_coloring = st.sidebar.checkbox("Enable Row Coloring", value=True)
    
    ip_color_map = {}
    if 'IP Type' in filtered_df.columns:
        ip_types = sorted(filtered_df['IP Type'].dropna().unique())
        for ip in ip_types:
            col1, col2 = st.sidebar.columns([1, 4])
            with col1:
                ip_color_map[ip] = st.color_picker("", "#ffffff", key=f"color_{ip}")
            with col2:
                st.markdown(f"<div style='margin-top: 8px'>{ip}</div>", unsafe_allow_html=True)
else:
    enable_coloring = False
    ip_color_map = {}
