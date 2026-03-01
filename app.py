from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import json

app = Flask(__name__)
CORS(app)

# Simple JD Analysis function
def analyze_jd(jd_text):
    """Analyze job description and extract key information"""
    if not jd_text or not isinstance(jd_text, str):
        return {"error": "Invalid input"}
    
    # Extract basic info
    lines = jd_text.split('\n')
    word_count = len(jd_text.split())
    line_count = len(lines)
    
    # Extract potential requirements (lines containing keywords)
    requirements = []
    req_keywords = ['require', 'must', 'should', 'need', 'experience', 'skill', 'qualification']
    for line in lines:
        if any(keyword in line.lower() for keyword in req_keywords):
            requirements.append(line.strip())
    
    # Extract potential responsibilities
    responsibilities = []
    resp_keywords = ['responsibilit', 'duties', 'task', 'role', 'function']
    for line in lines:
        if any(keyword in line.lower() for keyword in resp_keywords):
            responsibilities.append(line.strip())
    
    return {
        "word_count": word_count,
        "line_count": line_count,
        "requirements": requirements[:10],  # Limit to first 10
        "responsibilities": responsibilities[:10],  # Limit to first 10
        "summary": f"Job description contains {word_count} words across {line_count} lines."
    }

# Simple Keyword Generation function
def generate_keywords(jd_text):
    """Generate relevant keywords from job description"""
    if not jd_text or not isinstance(jd_text, str):
        return {"error": "Invalid input"}
    
    # Extract words and filter
    words = re.findall(r'\b[A-Za-z]{3,}\b', jd_text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
        'did', 'she', 'use', 'any', 'way', 'too', 'own', 'say', 'per', 'man',
        'put', 'set', 'yet', 'big', 'few', 'let', 'end', 'far', 'ask', 'men',
        'saw', 'run', 'god', 'air', 'box', 'eye', 'cup', 'job', 'key', 'top'
    }
    
    # Filter and count words
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [word for word, freq in sorted_words[:20]]
    
    return {
        "keywords": top_keywords,
        "total_unique_words": len(word_freq),
        "message": f"Generated {len(top_keywords)} keywords from the job description."
    }

# Simple Resume Matching function
def match_resume(jd_text, resume_text):
    """Match resume against job description"""
    if not jd_text or not resume_text or not isinstance(jd_text, str) or not isinstance(resume_text, str):
        return {"error": "Invalid input"}
    
    # Extract keywords from both
    jd_keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', jd_text.lower()))
    resume_keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', resume_text.lower()))
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
        'did', 'she', 'use', 'any', 'way', 'too', 'own', 'say', 'per', 'man',
        'put', 'set', 'yet', 'big', 'few', 'let', 'end', 'far', 'ask', 'men',
        'saw', 'run', 'god', 'air', 'box', 'eye', 'cup', 'job', 'key', 'top'
    }
    
    jd_keywords = jd_keywords - stop_words
    resume_keywords = resume_keywords - stop_words
    
    # Calculate match
    common_keywords = jd_keywords.intersection(resume_keywords)
    match_percentage = 0
    if len(jd_keywords) > 0:
        match_percentage = round((len(common_keywords) / len(jd_keywords)) * 100, 2)
    
    return {
        "match_percentage": match_percentage,
        "common_keywords": list(common_keywords)[:15],
        "jd_keywords_count": len(jd_keywords),
        "resume_keywords_count": len(resume_keywords),
        "message": f"Resume matches {match_percentage}% of the job description keywords."
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze-jd', methods=['POST'])
def api_analyze_jd():
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '')
        result = analyze_jd(jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/generate-keywords', methods=['POST'])
def api_generate_keywords():
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '')
        result = generate_keywords(jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/match-resume', methods=['POST'])
def api_match_resume():
    try:
        data = request.get_json()
        jd_text = data.get('jd_text', '')
        resume_text = data.get('resume_text', '')
        result = match_resume(jd_text, resume_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
