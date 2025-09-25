# Legal Contract Intelligence (NLP Powered)

A Streamlit-based Python application to analyze legal contracts.  
It allows users to **upload a legal contract PDF**, then automatically:

- Extract **key clauses** (Termination, Liability, Confidentiality, Payment, Governing Law, Dispute)  
- Generate a **summary** of the contract  
- Perform a **risk analysis**  
- Create a **compliance checklist**

This project uses **NLP** (`spaCy` + `NLTK`) for clause extraction and summarization.

---

## Features

1. **Upload legal contracts (PDF)**  
2. **NLP-based clause extraction**  
3. **Smart summary of the contract**  
4. **Risk analysis** based on key clauses  
5. **Compliance checklist** for easy review  

---

## Requirements

- Python 3.8+  
- `streamlit`  
- `pdfplumber`  
- `spacy`  
- `nltk`  
- `pandas` (optional, for table display)  

---

## Setup Instructions

1. **Clone the repository** (or download the code):



Create a virtual environment (recommended):

python -m venv venv


Activate the virtual environment:

Windows:

venv\Scripts\activate


Linux / Mac:

source venv/bin/activate


Install dependencies:

pip install streamlit pdfplumber spacy nltk pandas


Download spaCy English model:

python -m spacy download en_core_web_sm


Download NLTK punkt tokenizer (used for sentence tokenization):

This will happen automatically in the app, but you can do it manually in Python:

import nltk
nltk.download('punkt')

Running the App

Ensure your virtual environment is activated.

Run the Streamlit app:

streamlit run app.py


Open the URL displayed in the terminal, usually:

Local URL: http://localhost:8501


Upload a legal contract PDF to view:

Contract summary

Extracted key clauses

Risk analysis

Compliance checklist

Sample Input

You can test the app with a sample legal contract paragraph:

This Agreement is entered into on the 1st day of January 2025, by and between ABC Corporation ("Company") and Jo

```bash
git clone <repository-url>
cd legal_contract_intelligence
