# 🧠 Pybase-AI: AI-Powered Python Code Reviewer
Pybase-AI is a comprehensive Python code reviewer that combines traditional static analysis tools with generative AI to automate code reviews and improve code quality. Built during the Elevate Labs Internship Program, this tool aims to help developers write cleaner, more secure, and well-documented code.

## 🔍 Features
- Black Formatter – Auto-format Python code for consistency.
- Flake8 Linting – Check for PEP8 and style violations.
- Cyclomatic Complexity – Visualize complexity per function using Radon.
- Maintainability Index & Metrics – Understand maintainability and code structure.
- Security Scanning – Detect vulnerabilities using Bandit.
- Documentation Coverage – Analyze comment and docstring ratio.
- AI-Powered Suggestions – Gemini/OpenAI suggests improvements, refactoring, and better practices.
- Unit Test Generator – Generate basic Pytest unit tests using AI.
- Inline AI Review Comments – Annotate code with AI reviewer-style suggestions.
- Downloadable Text Reports – Full analysis ready for archiving or sharing.

## 🧰 Tech Stack

| Layer | Technology |
| ------------- |:-------------:|
| Frontend | Streamlit, Plotly |
| Backend | Python |
| AI/LLM | Gemini API |
| Static Analysis | flake8, black, radon, bandit |
| Testing | pytest |
| Data Visualization | Plotly Express |

## 🚀 Demo
- 🔗 [Try the Live App](https://pybase-review.streamlit.app/)

- 📂 [View the Source Code](https://github.com/RohitBhavsar27/ai-code-reviewer)

## 📦 Installation
```
git clone https://github.com/RohitBhavsar27/ai-code-reviewer.git
cd ai-code-reviewer
pip install -r requirements.txt
streamlit run app.py
```

## 🔐 Setup
- Create a .streamlit/secrets.toml file:
```
GEMINI_API_KEY = "your_gemini_api_key"
```

## 👥 Team & Credits
This project was built by Rohit Bhavsar as part of the Elevate Labs Virtual Internship Program (2025).
Special thanks to the mentors and the Elevate community for their support and feedback.
