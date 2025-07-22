# reviewer.py

import subprocess
import tempfile
import os
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
from radon.visitors import Function
import black
import tempfile
import subprocess
import os
import json
import google.generativeai as genai
from functools import lru_cache
import streamlit as st
import os
import os


@lru_cache(maxsize=32)
def run_flake8(code: str) -> str:
    """Run flake8 on the given code and return output as string."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(["flake8", tmp_path], capture_output=True, text=True)
        return result.stdout or "No linting issues found."
    finally:
        os.remove(tmp_path)


def run_black_diff(code: str) -> str:
    """Show how black would format the code."""
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        if code == formatted_code:
            return "Code is already well-formatted ✅"
        else:
            return f"--- Original ---\n{code}\n\n--- Formatted by black ---\n{formatted_code}"
    except Exception as e:
        return f"Black formatting error: {e}"

@lru_cache(maxsize=32)
def run_black_format(code: str) -> str:
    """Formats the code using black and returns the formatted code."""
    try:
        return black.format_str(code, mode=black.Mode())
    except Exception as e:
        return f"Black formatting error: {e}"




@lru_cache(maxsize=32)
def run_radon_complexity(code: str) -> str:
    """Calculate cyclomatic complexity of the code."""
    try:
        blocks = cc_visit(code)
        if not blocks:
            return "No functions/methods to analyze complexity."
        output = []
        for block in blocks:
            if isinstance(block, Function):
                output.append(
                    f"{block.name} - Complexity: {block.complexity} (Line {block.lineno})"
                )
        return "\n".join(output)
    except Exception as e:
        return f"Radon complexity error: {e}"


@lru_cache(maxsize=32)
def get_complexity_data(code: str):
    """Return function names and complexity scores for charting."""
    try:
        blocks = cc_visit(code)
        labels = [b.name for b in blocks]
        values = [b.complexity for b in blocks]
        return labels, values
    except Exception as e:
        return [], []


@lru_cache(maxsize=32)
def run_radon_metrics(code: str) -> str:
    """Calculate maintainability index and raw metrics."""
    try:
        mi = mi_visit(code, True)
        raw = analyze(code)
        return f"Maintainability Index: {mi:.2f}\nLines: {raw.loc}, Comments: {raw.comments}, Blank lines: {raw.blank}"
    except Exception as e:
        return f"Radon metrics error: {e}"


@lru_cache(maxsize=32)
def calculate_doc_ratio(code: str) -> str:
    """Calculate ratio of comments and docstrings to code lines."""
    lines = code.splitlines()
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    docstring_lines = sum(1 for line in lines if '"""' in line or "'''" in line)

    ratio = (comment_lines + docstring_lines) / total_lines if total_lines else 0
    percent = round(ratio * 100, 2)

    return f"📚 Documentation Coverage: {percent}% ({comment_lines} comments, {docstring_lines} docstring lines out of {total_lines} total lines)"


@lru_cache(maxsize=32)
def run_bandit_scan(code: str) -> str:
    """Run bandit security scan on code and return results."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["bandit", "-q", tmp_path], capture_output=True, text=True
        )
        return result.stdout or "✅ No security issues found by Bandit."
    except Exception as e:
        return f"Bandit scan error: {e}"
    finally:
        os.remove(tmp_path)




@lru_cache(maxsize=32)
def get_ai_suggestions(code: str) -> list[dict]:
    """Use Gemini to provide code improvement suggestions in a structured format."""
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Review the following Python code and provide suggestions for improvement,
        refactoring, naming, readability, and performance.
        Return the suggestions as a JSON array of objects, where each object has 'line' (int) and 'suggestion' (str) keys.
        If a suggestion applies to the whole file, use line 0.

        Example:
        [{{"line": 5, "suggestion": "Add a docstring."}}, {{"line": 10, "suggestion": "Optimize this loop."}}]

        {code}
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Attempt to extract JSON from a code block
            if response_text.startswith("```json") and response_text.endswith("```"):
                json_str = response_text[len("```json"): -len("```")].strip()
            else:
                json_str = response_text

            try:
                suggestions = json.loads(json_str)
                return suggestions
            except json.JSONDecodeError:
                if attempt == max_retries - 1:
                    return [{"line": 0, "suggestion": "AI suggestions could not be parsed after multiple attempts. Original response: " + response_text}]
    except Exception as e:
        return [{"line": 0, "suggestion": f"Gemini error: {e}"}]

@lru_cache(maxsize=32)
def generate_unit_tests(code: str) -> str:
    """Use Gemini to generate basic unit tests for the given code using pytest."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Generate pytest unit tests for the following Python code. "
            "Focus on basic functionality and edge cases where applicable. "
            "Provide only the Python code for the tests, no explanations or extra text.\n\n" + code
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini test generation error: {e}"


def generate_text_report(code: str, ai_enabled: bool = True) -> str:

    """Generate a combined plain text report from all tools."""
    report = (
        "🧹 Black Format Suggestion:\n" + run_black_diff(code) + "\n\n"
        "🔧 Flake8 Linting Report:\n" + run_flake8(code) + "\n\n"
        "📊 Cyclomatic Complexity:\n" + run_radon_complexity(code) + "\n\n"
        "📈 Maintainability Metrics:\n" + run_radon_metrics(code) + "\n\n"
        "📚 Documentation Ratio:\n" + calculate_doc_ratio(code) + "\n\n"
        "🛡️ Security Scan (Bandit):\n" + run_bandit_scan(code) + "\n\n"
    )
    if ai_enabled:
        report += (
            "🤖 AI-Powered Suggestions:\n" + "\n".join([f"Line {s["line"]}: {s["suggestion"]}" for s in get_ai_suggestions(code)]) + "\n\n"
            "🧪 Generated Unit Tests:\n" + generate_unit_tests(code) + "\n\n"
        )
    else:
        report += (
            "🤖 AI-Powered Suggestions: AI mode is disabled.\n\n"
            "🧪 Generated Unit Tests: AI mode is disabled.\n\n"
        )
    return report


def interleave_comments_with_code(code: str, suggestions: list[dict]) -> str:
    """Interleave AI suggestions as comments within the code."""
    lines = code.splitlines()
    interleaved_lines = []
    suggestion_map = {s["line"]: s["suggestion"] for s in suggestions}

    for i, line in enumerate(lines):
        interleaved_lines.append(line)
        if (i + 1) in suggestion_map:
            interleaved_lines.append(f"# AI Suggestion: {suggestion_map[i+1]}")
    
    if 0 in suggestion_map:
        interleaved_lines.insert(0, f"# AI Suggestion (General): {suggestion_map[0]}")

    return "\n".join(interleaved_lines)
