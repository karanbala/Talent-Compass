import streamlit as st
import docx
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Read the content from a Word document
def read_document(file_path):
    doc = docx.Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return text

# Preprocess text to remove stop words and non-alphabetic characters
def preprocess_text(text):
    doc = nlp(text)
    tokens = [' '.join([token.lemma_.lower() for token in nlp(sentence) if not token.is_stop and token.is_alpha]) for sentence in text.split('.')]
    return ' '.join(tokens)

# Search for keywords in resume
def search_keywords_in_resume(resume_text, keywords):
    matches = [keyword for keyword in keywords if keyword in resume_text]
    return matches

# Calculate matching percentage
def calculate_matching_percentage(matches, total_keywords):
    unique_matches = set(matches)
    if total_keywords == 0:
        return 0.0
    percentage = (len(unique_matches) / total_keywords) * 100
    return percentage

st.title("Skill Sync Tool")

# File uploader
resume_file = st.file_uploader("Upload your resume", type="docx")

# Keywords input
input_keywords = st.text_input("Enter the keywords separated by commas")

if resume_file and input_keywords:
    # Read the resume
    resume_text_list = read_document(resume_file)
    resume_text = ' '.join(resume_text_list)

    # Preprocess resume text
    preprocessed_resume = preprocess_text(resume_text)

    # Process input keywords
    keywords = set([keyword.strip().lower() for keyword in input_keywords.split(',')])

    # Search for keywords in resume
    matches = search_keywords_in_resume(preprocessed_resume, keywords)

    # Calculate matching percentage
    matching_percentage = calculate_matching_percentage(matches, len(keywords))

    # Display results
    st.subheader("Matching Keywords Found in Resume")
    st.write(set(matches))

    st.subheader("Matching Percentage")
    st.write(f"{matching_percentage:.2f}%")
