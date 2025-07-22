import streamlit as st
import pandas as pd
import json
import docx2txt
import spacy
from spacy.matcher import Matcher
import re
import PyPDF2

from spacy.cli import download

# Download spaCy model
# download("en_core_web_sm")

# Load spaCy model
spacy.load("en_core_web_sm")

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error(
        "spaCy model not found. Please run 'python -m spacy download en_core_web_sm' to download it."
    )
    st.stop()

# Define regex patterns for contact info
PHONE_REGEX = re.compile(r"(\+?\d{1,3})?[-\s]?\d{10}")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Define keywords for sections
EDUCATION_KEYWORDS = ["education", "academic", "qualifications"]
EXPERIENCE_KEYWORDS = ["experience", "work history", "employment", "work experience"]
SKILL_KEYWORDS = ["skills", "abilities", "technical skills", "competencies"]
CERTIFICATION_KEYWORDS = [
    "certifications",
    "licenses",
    "honors",
    "awards",
    "certificate",
    "professional development",
    "courses",
    "training",
    "qualifications",
    "accreditations",
    "achievements",
]

ALL_SECTION_KEYWORDS = (
    EDUCATION_KEYWORDS
    + EXPERIENCE_KEYWORDS
    + SKILL_KEYWORDS
    + CERTIFICATION_KEYWORDS
    + [
        "summary",
        "objective",
        "projects",
        "publications",
        "volunteer",
        "interests",
        "references",
        "hobbies and interests",
        "declaration",
    ]
)


def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        print(
            f"Extracted {len(text)} characters from PDF ({len(pdf_reader.pages)} pages)."
        )
        return text
    except PyPDF2.errors.PdfReadError:
        st.error(
            f"Error: Could not read the PDF file '{file.name}'. It may be corrupted or encrypted."
        )
        return None
    except Exception as e:
        st.error(
            f"An unexpected error occurred while reading the PDF file '{file.name}': {e}"
        )
        return None


def extract_text_from_docx(file):
    try:
        return docx2txt.process(file)
    except Exception as e:
        st.error(f"Error reading DOCX file '{file.name}': {e}")
        return None


def extract_contact_info(text):
    phone_numbers = PHONE_REGEX.findall(text)
    emails = EMAIL_REGEX.findall(text)
    return {
        "Phone": ", ".join(phone_numbers) if phone_numbers else "Not Found",
        "Email": ", ".join(emails) if emails else "Not Found",
    }


def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not Found"


def extract_section(text, keywords):
    text_lower = text.lower()
    for keyword in keywords:
        # More flexible regex for section header, allowing other words on the line
        # and making it case-insensitive
        match = re.search(
            rf"^\s*{re.escape(keyword)}.*$", text_lower, re.MULTILINE | re.IGNORECASE
        )
        if match:
            start_index = match.end()
            # Find the start of the next section using all known keywords, case-insensitive
            next_section_pattern = "|".join(
                [re.escape(k) for k in ALL_SECTION_KEYWORDS if k != keyword]
            )
            next_section_match = re.search(
                rf"^\s*({next_section_pattern}).*$",
                text_lower[start_index:],
                re.MULTILINE | re.IGNORECASE,
            )

            if next_section_match:
                end_index = start_index + next_section_match.start()
                print(
                    f"Found next section '{next_section_match.group(0)}' at index {end_index}"
                )
                return text[start_index:end_index].strip()
            else:
                print("No next section found, taking rest of the text.")
                return text[start_index:].strip()
    print(f"Keyword '{keyword}' not found as a section header.")
    return "Not Found"


def extract_skills(text):
    skills_section = extract_section(text, SKILL_KEYWORDS)
    if skills_section != "Not Found":
        return skills_section
    doc = nlp(text)
    skills = [
        ent.text for ent in doc.ents if ent.label_ in ["SKILL", "LANGUAGE", "TECH"]
    ]
    return ", ".join(skills) if skills else "Not Found"


def extract_education(text):
    return extract_section(text, EDUCATION_KEYWORDS)


def extract_experience(text):
    return extract_section(text, EXPERIENCE_KEYWORDS)


def extract_certifications(text):
    return extract_section(text, CERTIFICATION_KEYWORDS)


def parse_resume(text):
    contact_info = extract_contact_info(text)
    name = extract_name(text)
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    certifications = extract_certifications(text)
    print(f"Extracted Certifications: {certifications}")

    return {
        "Name": name,
        "Phone": contact_info["Phone"],
        "Email": contact_info["Email"],
        "Skills": skills,
        "Education": education,
        "Experience": experience,
        "Certifications": certifications,
    }


def main():
    st.set_page_config(
        page_title="Smart Resume Parser", page_icon=":page_facing_up:", layout="wide"
    )
    st.title("Smart Resume Parser")

    st.sidebar.header("Upload Resumes")
    uploaded_files = st.sidebar.file_uploader(
        "Choose PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True
    )

    if uploaded_files:
        all_data = []
        for file in uploaded_files:
            text = ""
            if file.type == "application/pdf":
                text = extract_text_from_pdf(file)
            elif (
                file.type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                text = extract_text_from_docx(file)

            if text:
                data = parse_resume(text)
                all_data.append(data)

        if all_data:
            df = pd.DataFrame(all_data)
            st.header("Parsed Resume Data")

            def highlight_not_found(val):
                color = "background-color: #ffcccc" if val == "Not Found" else ""
                return color

            st.dataframe(df.style.map(highlight_not_found))

            st.header("Export Data")
            col1, col2 = st.columns(2)

            with col1:
                json_data = df.to_json(orient="records")
                st.download_button(
                    "Download JSON",
                    json_data,
                    "resume_data.json",
                    "application/json",
                    use_container_width=True,
                )

            with col2:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv_data,
                    "resume_data.csv",
                    "text/csv",
                    use_container_width=True,
                )
    else:
        st.info("Please upload one or more resumes to get started.")


if __name__ == "__main__":
    main()
