import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request
import PyPDF2 as pdf
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_response(resume_text, jd_text):
    prompt = f"""
    Act as an expert Technical Human Resource Manager. 
    Evaluate the following resume against the job description.
    
    Resume content: {resume_text}
    Job Description content: {jd_text}
    
    Return a valid JSON object ONLY with this structure:
    {{
      "match_percentage": <number 0-100>,
      "missing_keywords": ["keyword1", "keyword2"],
      "profile_summary": "2-3 sentence summary",
      "improvement_tips": ["tip1", "tip2", "tip3"]
    }}
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            temperature=0.1
        )
    )
    return json.loads(response.text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        jd = request.form.get('jd')
        file = request.files.get('resume')
        
        if not file or file.filename == '':
            return render_template('index.html', error="No resume file uploaded.")

        reader = pdf.PdfReader(file)
        resume_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume_text += text
        
        if not resume_text.strip():
            return render_template('index.html', error="Could not extract text from PDF. It might be a scanned image.")

        analysis_result = get_gemini_response(resume_text, jd)
        
        return render_template('index.html', result=analysis_result)

    except Exception as e:
        return render_template('index.html', error=f"System Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)