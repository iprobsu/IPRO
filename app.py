import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill

if st.session_state.role in ["Moderator", "Admin"]:
    st.markdown("### ⬇️ Export Options")

    ip_options = sorted(filtered_df["IP Type"].dropna().unique())
    selected_types = st.multiselect("📑 Select IP Types to include in download", ip_options, default=ip_options)

    export_df = filtered_df[filtered_df["IP Type"].isin(selected_types)]

    if export_df.empty:
        st.warning("⚠️ No data to export with the selected IP Types.")
    else:
        to_export = export_df.copy()
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Filtered IP Records"

        # Write header
        ws.append(list(to_export.columns))

        # Row styling (only if enabled)
        for idx, row in to_export.iterrows():
            values = list(row.values)
            ws.append(values)

            if enable_coloring:
                ip = row.get("IP Type", "")
                hex_color = ip_color_map.get(ip, "#FFFFFF").replace("#", "")
                fill = PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")
                for col in range(1, len(values)+1):
                    ws.cell(row=idx+2, column=col).fill = fill  # +2 for header + 1-based index

        # Save to buffer
        wb.save(output)
        output.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (With Colors)" if enable_coloring else "⬇️ Download as Excel",
            data=output,
            file_name="filtered_ip_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
