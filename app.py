from flask import Flask, render_template, request
import PyPDF2 as pdf
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Setup
app = Flask(__name__)
nltk.download('punkt')
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def get_scores(resume_text, jd_text):
    # --- Formatting Score ---
    format_score = 0
    checks = {
        "Email": r'[\w\.-]+@[\w\.-]+',
        "Phone": r'\+?\d[\d\s.-]{8,}\d',
        "Experience": r'(?i)experience|work history',
        "Education": r'(?i)education|academic',
        "Skills": r'(?i)skills|technologies'
    }
    format_details = {k: bool(re.search(v, resume_text)) for k, v in checks.items()}
    format_score = sum(2 for found in format_details.values() if found)

    # --- Keyword Score ---
    res_tokens = {w for w in word_tokenize(resume_text.lower()) if w.isalnum() and w not in STOPWORDS}
    jd_tokens = {w for w in word_tokenize(jd_text.lower()) if w.isalnum() and w not in STOPWORDS}
    matched = res_tokens.intersection(jd_tokens)
    
    keyword_score = round((len(matched) / len(jd_tokens)) * 10) if jd_tokens else 0
    
    return {
        "total_score": format_score + keyword_score,
        "format_score": format_score,
        "format_details": format_details,
        "keyword_score": keyword_score,
        "matched_words": list(matched),
        "matched_count": len(matched)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    jd = request.form['jd']
    file = request.files['resume']
    
    # Read PDF
    reader = pdf.PdfReader(file)
    resume_text = ""
    for page in reader.pages:
        resume_text += page.extract_text()
    
    result = get_scores(resume_text, jd)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)