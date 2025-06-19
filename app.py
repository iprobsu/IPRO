# --- Display Results with Pastel Color Picker via Dropdown ---
if filtered_df.empty:
    st.warning("😕 No records matched your filters or search term.")
else:
    clean_df = filtered_df.dropna(axis=1, how='all')
    clean_df = clean_df.loc[:, ~(clean_df == '').all()]

    st.markdown(f"### 📄 Showing {len(clean_df)} result{'s' if len(clean_df) != 1 else ''}")

    # Button to reveal color settings
    show_colors = st.button("🎨 Customize Row Colors")

    if show_colors and 'IP Type' in clean_df.columns:
        ip_types = sorted(clean_df['IP Type'].dropna().unique())

        # Predefined pastel palette
        pastel_palette = {
            "Sky Blue": "#AEDFF7",
            "Mint Green": "#B2F2BB",
            "Lavender": "#E6CCFF",
            "Peach": "#FFD8BE",
            "Pale Yellow": "#FFFACD",
            "Soft Pink": "#FFCCE5",
            "Light Gray": "#E8E8E8",
            "None": "#FFFFFF"
        }

        st.markdown("**Select a pastel color for each IP Type:**")
        color_cols = st.columns(len(ip_types))

        selected_colors = {}
        for i, ip in enumerate(ip_types):
            with color_cols[i]:
                color_name = st.selectbox(
                    f"{ip}",
                    options=list(pastel_palette.keys()),
                    index=len(pastel_palette) - 1,
                    key=f"pastel_{ip}"
                )
                selected_colors[ip] = pastel_palette[color_name]

        # Apply color style to rows
        def style_rows(row):
            bg = selected_colors.get(row['IP Type'], '#FFFFFF')
            return [f'background-color: {bg}'] * len(row)

        styled_df = clean_df.style.apply(style_rows, axis=1)
        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.dataframe(clean_df, use_container_width=True, height=600)
