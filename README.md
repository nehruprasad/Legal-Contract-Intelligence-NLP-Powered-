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

```bash
git clone <repository-url>
cd legal_contract_intelligence
