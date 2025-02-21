import streamlit as st
import docx
import spacy
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import time

# Set the page configuration (title and favicon)
st.set_page_config(page_title="Talent Compass Skill Sync Tool", page_icon="icon.ico")

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Read the content from a Word document
def read_document(file_path):
    doc = docx.Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return ' '.join(text)

# Preprocess text to remove stop words and non-alphabetic characters
def preprocess_text(text):
    doc = nlp(text)
    tokens = [' '.join([token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha])]
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

# Custom CSS for colorful styling and animations using Animate.css
st.markdown("""
    <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');
        
        .sidebar .sidebar-content {
            background-color: #f5f5f5;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .main {
            background-color: #e3f2fd;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .title {
            font-family: 'Arial', sans-serif;
            color: #333;
            font-weight: bold;
            text-align: center;
            margin-top: 35px;
        }
        .subheader {
            font-family: 'Arial', sans-serif;
            color: #555;
        }
        .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 150px; /* Adjust the width to your preference */
        }
    </style>
""", unsafe_allow_html=True)

# Add your company logo to the sidebar
st.sidebar.image("logo.png", width=200)

st.title("Talent Compass Skill Sync Tool")

# File uploader and keyword input in the sidebar
#st.sidebar.title("Talent Compass Skill Sync Tool")
st.sidebar.write("Upload your resumes and enter keywords to find the best match.")
resume_files = st.sidebar.file_uploader("Upload your resumes", type="docx", accept_multiple_files=True)
input_keywords = st.sidebar.text_input("Enter the keywords separated by commas")
min_percentage = st.sidebar.slider("Minimum Matching Percentage", 0, 100, 50)

tab1, tab2, tab3 = st.tabs(["Upload", "Keywords", "Results"])

with tab1:
    st.subheader("Upload Resumes")
    st.write("Please upload your resumes using the sidebar.")

with tab2:
    st.subheader("Enter Keywords")
    st.write("Enter the keywords you want to match with your resumes using the sidebar.")

if resume_files and input_keywords:
    # Process input keywords
    keywords = set([keyword.strip().lower() for keyword in input_keywords.split(',')])
    
    best_match_percentage = 0
    best_match_file = None
    results = []
    
    # Progress bar
    progress_bar = st.progress(0)
    progress_step = 1.0 / len(resume_files)
    current_progress = 0
    
    for resume_file in resume_files:
        # Read the resume
        resume_text = read_document(resume_file)
        
        # Preprocess resume text
        preprocessed_resume = preprocess_text(resume_text)
        
        # Search for keywords in resume
        matches = search_keywords_in_resume(preprocessed_resume, keywords)
        
        # Calculate matching percentage
        matching_percentage = calculate_matching_percentage(matches, len(keywords))
        
        results.append({"Resume": resume_file.name, "Matching Percentage": matching_percentage, "Matched Keywords": ', '.join(matches)})
        
        if matching_percentage > best_match_percentage:
            best_match_percentage = matching_percentage
            best_match_file = resume_file.name
        
        current_progress += progress_step
        progress_bar.progress(min(current_progress, 1.0))
        time.sleep(0.1)  # Simulate some processing time
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Filter results based on minimum matching percentage
    filtered_results_df = results_df[results_df["Matching Percentage"] >= min_percentage]
    
    # Display results in a table with sorting options
    st.markdown(f"""
        <div class="main animate__animated animate__fadeInUp">
            <h2 class="title">Results</h2>
    """, unsafe_allow_html=True)
    
    gb = GridOptionsBuilder.from_dataframe(filtered_results_df)
    gb.configure_pagination()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
    gridOptions = gb.build()
    
    AgGrid(filtered_results_df, gridOptions=gridOptions, enable_enterprise_modules=True)
    
    # Display the best match
    st.subheader("Best Matching Resume")
    st.write(f"The resume with the highest matching percentage is: **{best_match_file}**")
    st.write(f"Matching Percentage: **{best_match_percentage:.2f}%**")
    
    # Provide an option to download the filtered results as a CSV file
    st.download_button(
        label="Download Filtered Results as CSV",
        data=filtered_results_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_results.csv",
        mime="text/csv"
    )
