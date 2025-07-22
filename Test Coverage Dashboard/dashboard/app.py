import streamlit as st
import json
import pandas as pd
import os

# Set Streamlit page config
st.set_page_config(
    page_title="Test Coverage Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Interactive Test Coverage Dashboard")

# 1. Dynamic File Upload
uploaded_file = st.file_uploader("Choose a coverage.json file", type="json")

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid coverage.json.")
        st.stop()

    files_data = data.get("files", {})
    if not files_data:
        st.warning("No file coverage data found in the uploaded file.")
        st.stop()

    file_coverage_details = []
    for filepath, info in files_data.items():
        summary = info["summary"]
        file_coverage_details.append(
            {
                "File Name": os.path.basename(filepath),
                "Covered Lines": summary["covered_lines"],
                "Total Lines": summary["num_statements"],
                "Uncovered Lines": summary["missing_lines"],
                "Coverage %": (
                    (summary["covered_lines"] / summary["num_statements"]) * 100
                    if summary["num_statements"] > 0
                    else 0
                ),
            }
        )

    coverage_df = pd.DataFrame(file_coverage_details)

    # 6. Overall Coverage Metric
    total_statements = coverage_df["Total Lines"].sum()
    total_covered = coverage_df["Covered Lines"].sum()
    overall_percent = (
        (total_covered / total_statements) * 100 if total_statements > 0 else 0
    )

    st.metric("Overall Test Coverage", f"{overall_percent:.2f}%")

    st.markdown("---")

    # 2. Highlight Low Coverage Files
    low_coverage_files = coverage_df[coverage_df["Coverage %"] < 50]
    if not low_coverage_files.empty:
        with st.expander("🚨 Files with Low Coverage (< 50%)", expanded=True):
            st.dataframe(
                low_coverage_files.style.format(
                    {"Coverage %": "{:.2f}%"}
                ).highlight_max(axis=0, color="#ff4d4d"),
                use_container_width=True,
            )

    # 3. Bar Chart Visualization
    st.subheader("📁 File-wise Coverage (%)")

    def get_color(percent):
        if percent < 50:
            return "#ff4d4d"  # Red
        elif percent < 80:
            return "#ffc107"  # Amber
        else:
            return "#28a745"  # Green

    coverage_df["color"] = coverage_df["Coverage %"].apply(get_color)
    st.bar_chart(
        coverage_df,
        x="File Name",
        y="Coverage %",
        color="color",
        height=400,
        use_container_width=True,
    )

    # 4. Tabular Breakdown
    st.subheader("📄 Detailed Coverage Breakdown")
    st.dataframe(
        coverage_df.drop(columns=["color"]).style.format({"Coverage %": "{:.2f}%"}),
        use_container_width=True,
    )

    # 5. CSV Export
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(coverage_df.drop(columns=["color"]))

    st.download_button(
        label="📥 Download Coverage Report as CSV",
        data=csv,
        file_name="coverage_report.csv",
        mime="text/csv",
    )

else:
    st.info("Upload a `coverage.json` file to get started.")
