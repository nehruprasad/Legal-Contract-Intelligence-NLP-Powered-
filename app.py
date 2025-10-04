import streamlit as st
import io
import re
import json
from collections import Counter

# Optional libraries (used if installed)
try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import docx2txt
except Exception:
    docx2txt = None

try:
    from transformers import pipeline
    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False

# ----------------- Helpers -----------------
KEY_CLAUSES = [
    'confidentiality', 'termination', 'indemnity', 'liability', 'governing law',
    'jurisdiction', 'payment', 'intellectual property', 'warranty', 'data protection',
    'force majeure', 'assignment', 'non-compete', 'dispute resolution', 'privacy'
]

RISK_KEYWORDS = {
    'high': ['no liability', 'sole remedy', 'exclusive remedy', 'liquidated damages', 'penalty', 'irrevocable'],
    'medium': ['indemnify', 'third party', 'limitations of liability', 'cap on liability', 'breach'],
    'low': ['governing law', 'jurisdiction', 'notice', 'term', 'payment']
}


def extract_text_from_pdf(file_bytes):
    if pdfplumber is None:
        st.warning("pdfplumber not installed — please install it (pip install pdfplumber) for better PDF extraction.")
        return file_bytes.decode('utf-8', errors='ignore') if isinstance(file_bytes, (bytes, bytearray)) else str(file_bytes)
    text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
    return '\n'.join(text)


def extract_text_from_docx(file_bytes):
    if docx2txt is None:
        st.warning("docx2txt not installed — please install it (pip install docx2txt) for DOCX extraction.")
        return file_bytes.decode('utf-8', errors='ignore') if isinstance(file_bytes, (bytes, bytearray)) else str(file_bytes)
    # docx2txt requires a file path, so write to a temp file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        text = docx2txt.process(tmp.name)
    return text


def extract_text(uploaded_file):
    if uploaded_file is None:
        return ''
    content = uploaded_file.read()
    name = uploaded_file.name.lower()
    if name.endswith('.pdf'):
        return extract_text_from_pdf(content)
    elif name.endswith('.docx') or name.endswith('.doc'):
        return extract_text_from_docx(content)
    else:
        try:
            return content.decode('utf-8')
        except Exception:
            return str(content)


def clean_text(text):
    # Remove non-ASCII characters (Chinese, Japanese, etc.)
    return re.sub(r'[^\x00-\x7F]+', ' ', text)


def split_into_clauses(text):
    # Heuristic splitting: look for headings or numbered sections
    clauses = []
    parts = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    for p in parts:
        subparts = re.split(r'(?m)^(?:[A-Z][A-Za-z\s]{1,50}:|Section\s+\d+\.?\d*\s*[:\-]?)', p)
        for s in subparts:
            if s.strip():
                clauses.append(s.strip())
    if not clauses:
        clauses = re.split(r'(?<=[.!?])\s+', text)
    return clauses


def find_key_clauses(clauses):
    found = {}
    lc_clauses = [c.lower() for c in clauses]
    for key in KEY_CLAUSES:
        matches = []
        for i, c in enumerate(lc_clauses):
            if key in c or any(word in c for word in key.split()):
                matches.append({'index': i, 'text': clauses[i]})
        if matches:
            found[key] = matches
    return found


def simple_summary(text, num_sentences=5):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= num_sentences:
        return ' '.join(sentences)
    words = re.findall(r'\w+', text.lower())
    freq = Counter(words)
    scores = []
    for s in sentences:
        s_words = re.findall(r'\w+', s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        scores.append((score, s))
    top = sorted(scores, key=lambda x: x[0], reverse=True)[:num_sentences]
    return ' '.join([s for _, s in top])


def analyze_risks(found_clauses):
    report = {}
    overall_score = 0
    for key, matches in found_clauses.items():
        clause_text = ' '.join([m['text'] for m in matches])
        score = 0
        reasons = []
        for lvl, kwlist in RISK_KEYWORDS.items():
            for kw in kwlist:
                if kw in clause_text.lower():
                    if lvl == 'high':
                        score += 3
                        reasons.append(f'High-risk keyword: "{kw}"')
                    elif lvl == 'medium':
                        score += 2
                        reasons.append(f'Medium-risk keyword: "{kw}"')
                    else:
                        score += 1
                        reasons.append(f'Low-risk keyword: "{kw}"')
        report[key] = {'score': score, 'reasons': list(set(reasons)), 'text': clause_text}
        overall_score += score
    report['overall_risk_score'] = overall_score
    return report


def build_compliance_checklist(found_clauses):
    checklist = []
    for key in KEY_CLAUSES:
        present = key in found_clauses and len(found_clauses[key]) > 0
        checklist.append({'item': key, 'present': present, 'notes': ''})
    return checklist

# ----------------- Optional: use transformers if available -----------------
SUMMARIZER = None

def hf_summarize(text, max_length=150, min_length=40):
    global SUMMARIZER
    if not HF_AVAILABLE:
        return simple_summary(text)
    if SUMMARIZER is None:
        try:
            # Force English summarization model
            SUMMARIZER = pipeline('summarization', model='facebook/bart-large-cnn')
        except Exception:
            return simple_summary(text)
    try:
        out = SUMMARIZER(text, max_length=max_length, min_length=min_length)
        return out[0]['summary_text']
    except Exception:
        return simple_summary(text)

# ----------------- Streamlit App -----------------
st.set_page_config(page_title="Legal Contract Intelligence", layout='wide')
st.title("📄 Legal Contract Intelligence")
st.markdown("Upload a contract (PDF, DOCX, TXT) to extract key clauses, get a summary, risk analysis, and a compliance checklist.")

with st.sidebar:
    st.header("Settings")
    use_hf = st.checkbox('Use HuggingFace summarizer (if available)', value=False)
    num_summary_sentences = st.slider('Summary sentences (extractive fallback)', 3, 10, 5)
    show_raw = st.checkbox('Show raw extracted text', value=False)

uploaded = st.file_uploader("Upload contract file", type=['pdf', 'docx', 'doc', 'txt'])

if uploaded:
    raw_text = extract_text(uploaded)
    raw_text = clean_text(raw_text)

    if show_raw:
        st.subheader('Raw extracted text')
        st.text_area('Raw text', raw_text[:100000], height=300)

    st.subheader('Clause Extraction')
    clauses = split_into_clauses(raw_text)
    st.write(f"Detected {len(clauses)} text blocks/clauses (heuristic split)")

    found = find_key_clauses(clauses)
    if not found:
        st.info('No common key clauses detected by heuristics. You can search manually below or toggle different settings.')

    for key, items in found.items():
        with st.expander(f"{key.title()} ({len(items)} match(es))", expanded=False):
            for it in items:
                st.write(it['text'])

    st.subheader('Summary')
    if use_hf and HF_AVAILABLE:
        summary = hf_summarize(raw_text, max_length=200, min_length=40)
    else:
        summary = simple_summary(raw_text, num_sentences=num_summary_sentences)
    st.write(summary)

    st.subheader('Risk Analysis')
    risk_report = analyze_risks(found)
    overall = risk_report.pop('overall_risk_score', 0)
    st.metric('Overall risk score (heuristic)', overall)
    for k, v in risk_report.items():
        with st.expander(f"{k.title()} — score: {v['score']}"):
            st.write('Reasons:')
            for r in v['reasons']:
                st.write('-', r)
            st.write('\nClause text:')
            st.write(v['text'][:500])

    st.subheader('Compliance Checklist')
    checklist = build_compliance_checklist(found)
    for item in checklist:
        st.checkbox(item['item'].title(), value=item['present'])

    st.subheader('Interactive Search')
    query = st.text_input('Search for clause or keyword')
    if query:
        hits = [c for c in clauses if query.lower() in c.lower()]
        st.write(f'Found {len(hits)} matches')
        for h in hits:
            st.write(h)

    st.subheader('Export Report')
    if st.button('Generate JSON report'):
        report = {
            'summary': summary,
            'found_clauses': found,
            'risk_report': risk_report,
            'overall_risk_score': overall,
            'checklist': checklist
        }
        st.download_button('Download report (JSON)', data=json.dumps(report, indent=2), file_name='contract_report.json', mime='application/json')

else:
    st.info('Upload a PDF / DOCX / TXT file to begin analysis.')

st.markdown('\n---\n')
st.caption('This tool is a prototype and not legal advice. For binding legal interpretation, consult a qualified attorney.')
