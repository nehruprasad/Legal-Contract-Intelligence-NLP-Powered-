import streamlit as st
import pdfplumber
import spacy
from nltk.tokenize import sent_tokenize

# Download NLTK punkt tokenizer if not already installed
import nltk
nltk.download('punkt')

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Keywords for clause detection
CLAUSE_KEYWORDS = ["termination", "liability", "confidentiality", "governing law", "payment", "dispute"]

# ----------------- Helper Functions -----------------

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_clauses_nlp(text):
    """
    Extract clauses using NLP: find sentences containing key keywords.
    """
    clauses = {}
    sentences = sent_tokenize(text)
    for keyword in CLAUSE_KEYWORDS:
        keyword_sentences = [s for s in sentences if keyword.lower() in s.lower()]
        if keyword_sentences:
            clauses[keyword.capitalize()] = keyword_sentences
    return clauses

def summarize_contract_nlp(text, max_sentences=5):
    """
    Simple NLP-based summary: pick first few sentences containing key keywords
    """
    sentences = sent_tokenize(text)
    # Score sentences by number of keywords present
    scored_sentences = []
    for s in sentences:
        score = sum([s.lower().count(k.lower()) for k in CLAUSE_KEYWORDS])
        if score > 0:
            scored_sentences.append((score, s))
    scored_sentences.sort(reverse=True)
    summary_sentences = [s for score, s in scored_sentences[:max_sentences]]
    if not summary_sentences:
        summary_sentences = sentences[:max_sentences]
    return " ".join(summary_sentences)

def risk_analysis_nlp(clauses):
    """
    Basic NLP-based risk assessment based on presence/absence of key clauses
    """
    risks = {}
    for key, content in clauses.items():
        if key.lower() in ["liability", "termination"]:
            risks[key] = "High risk" if len(content) > 1 else "Moderate risk"
        else:
            risks[key] = "Check compliance"
    return risks

def generate_compliance_checklist_nlp(clauses):
    checklist = {key: "✅ Present" if content else "❌ Missing" for key, content in clauses.items()}
    return checklist

# ----------------- Streamlit App -----------------

st.set_page_config(page_title="Legal Contract Intelligence (NLP)", layout="wide")
st.title("📄 Legal Contract Intelligence (NLP Powered)")

# Upload PDF
uploaded_file = st.file_uploader("Upload a legal contract (PDF)", type="pdf")

if uploaded_file:
    with open("temp_contract.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("File uploaded successfully!")

    # Extract text
    text = extract_text_from_pdf("temp_contract.pdf")
    
    # Contract summary
    st.header("📑 Contract Summary")
    summary = summarize_contract_nlp(text)
    st.write(summary)
    
    # Key clauses
    st.header("⚖️ Key Clauses (NLP)")
    clauses = extract_clauses_nlp(text)
    if clauses:
        for key, content in clauses.items():
            st.subheader(key)
            for c in content:
                st.write("- " + c)
    else:
        st.write("No key clauses detected.")

    # Risk analysis
    st.header("⚠️ Risk Analysis (NLP)")
    risks = risk_analysis_nlp(clauses)
    for key, risk in risks.items():
        st.write(f"{key}: {risk}")
    
    # Compliance checklist
    st.header("✅ Compliance Checklist (NLP)")
    checklist = generate_compliance_checklist_nlp(clauses)
    st.table(checklist)
