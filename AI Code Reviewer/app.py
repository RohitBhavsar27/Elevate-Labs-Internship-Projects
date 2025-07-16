# app.py

import streamlit as st
import plotly.express as px
from reviewer import (
    run_flake8,
    run_radon_complexity,
    run_radon_metrics,
    run_bandit_scan,
    get_ai_suggestions,
    generate_text_report,
    get_complexity_data,
    calculate_doc_ratio,
    generate_unit_tests,
    interleave_comments_with_code,
    run_black_format,
)

st.set_page_config(page_title="Pybase - AI Code Reviewer", layout="wide")

# Initialize session state for review status and report content
if "review_performed" not in st.session_state:
    st.session_state.review_performed = False
if "report_content" not in st.session_state:
    st.session_state.report_content = ""
if "code_to_review" not in st.session_state:
    st.session_state.code_to_review = ""
if "ai_suggestions" not in st.session_state:
    st.session_state.ai_suggestions = []

st.title("🧠 Pybase - AI Code Reviewer")
st.write(
    "Upload or paste Python code below to get an automated review using flake8, black, and radon."
)

# Choose input method
input_method = st.radio("Choose Input Method:", ("Paste Code", "Upload File"))

ai_enabled = st.checkbox("Enable AI Suggestions (requires API credits)", value=True)

# Main panel
st.header("Code Input")


# Handle input
code = ""

if input_method == "Paste Code":
    code = st.text_area("Paste your Python code here:", height=300, key="code_input")
elif input_method == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload a Python (.py) file", type=["py"], key="file_uploader"
    )
    if uploaded_file:
        code = uploaded_file.read().decode("utf-8")

# If code input is cleared, reset session state
if not code.strip() and st.session_state.review_performed:
    st.session_state.review_performed = False
    st.session_state.report_content = ""
    st.session_state.code_to_review = ""
    st.session_state.ai_suggestions = []


# Analyze button
if st.button("🔍 Analyze Code"):
    if code.strip():
        with st.spinner("Analyzing code..."):
            st.session_state.code_to_review = code
            st.session_state.review_performed = True
            if ai_enabled:
                st.session_state.ai_suggestions = get_ai_suggestions(code)
                st.session_state.report_content = generate_text_report(code, ai_enabled=ai_enabled)
            else:
                st.session_state.ai_suggestions = []
                st.session_state.report_content = generate_text_report(code, ai_enabled=False)
                st.info("AI mode is disabled. Showing only static analysis results.")
    else:
        st.warning("Please paste or upload some Python code first.")
        st.session_state.review_performed = False

if st.session_state.review_performed:
    st.download_button(
        label="📥 Download Report",
        data=st.session_state.report_content,
        file_name="code_review_report.txt",
        mime="text/plain",
    )

# Display review results if a review has been performed
if st.session_state.review_performed:
    code = st.session_state.code_to_review  # Use the stored code for displaying results
    suggestions = st.session_state.ai_suggestions  # Use stored AI suggestions

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Formatted Code", "Linting & Complexity", "Metrics & Security", 
        "AI Suggestions", "Unit Tests", "Full Report"
    ])

    with tab1:
        st.subheader("Black Formatter")
        formatted_code = run_black_format(code)
        st.code(formatted_code, language="python")

    with tab2:
        st.subheader("Flake8 Linting")
        st.code(run_flake8(code), language="text")
        
        st.subheader("Cyclomatic Complexity (Radon)")
        st.code(run_radon_complexity(code), language="text")
        labels, values = get_complexity_data(code)
        if labels:
            fig = px.bar(
                x=labels,
                y=values,
                labels={"x": "Function", "y": "Complexity"},
                title="Cyclomatic Complexity per Function",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No functions detected for complexity visualization.")

    with tab3:
        st.subheader("Maintainability Index & Metrics")
        st.code(run_radon_metrics(code), language="text")

        st.subheader("Documentation Ratio")
        st.success(calculate_doc_ratio(code))

        st.subheader("Security Scan (Bandit)")
        st.code(run_bandit_scan(code), language="text")

    if ai_enabled:
        with tab4:
            st.subheader("🤖 AI-Powered Suggestions")
            with st.expander("View Code with Inline AI Suggestions"):
                interleaved_code = interleave_comments_with_code(code, suggestions)
                st.code(interleaved_code, language="python")

        with tab5:
            st.subheader("🧪 Unit Test Generator")
            if st.button("Generate Unit Tests"):
                with st.spinner("Generating unit tests..."):
                    unit_tests = generate_unit_tests(code)
                st.code(unit_tests, language="python")
    else:
        with tab4:
            st.info("AI-Powered Suggestions are disabled. Enable AI mode to view.")
        with tab5:
            st.info("Unit Test Generation is disabled. Enable AI mode to view.")

    with tab6:
        st.subheader("Full Text Report")
        st.text(st.session_state.report_content)


# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>Pybase - AI Code Reviewer | Automating Python code review using industry-standard tools and generative AI.</p>",
    unsafe_allow_html=True,
)
