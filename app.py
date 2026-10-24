"""
ResumeIQ - Flask Application Entrypoint
AI-Powered Resume Analysis, Extraction & ATS Job Matching Platform.
"""

import os
import json
import traceback
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from config import Config
from core.parser import extract_text_from_file
from core.cleaner import clean_text, compute_word_frequencies
from core.extractor import ResumeExtractor
from core.scorer import ResumeScorer
from core.jd_matcher import JDMatcher
from core.feedback import generate_feedback

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError("Set SECRET_KEY as an environment variable before starting ResumeIQ.")

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    # -------------------------------------------------------------
    # WEB UI ROUTES
    # -------------------------------------------------------------
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/match')
    def match_page():
        return render_template('jd_match.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/sample/<role>')
    def get_sample_resume(role):
        """Returns sample resume raw text for instant demo analysis."""
        role_map = {
            'swe': 'software_engineer.txt',
            'software-engineer': 'software_engineer.txt',
            'data-scientist': 'data_scientist.txt',
            'ai': 'data_scientist.txt'
        }
        filename = role_map.get(role.lower(), 'software_engineer.txt')
        path = os.path.join(app.config['SAMPLE_DIR'], filename)

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({"status": "success", "role": role, "text": content})
        return jsonify({"status": "error", "message": "Sample not found"}), 404

    # -------------------------------------------------------------
    # API ENDPOINTS
    # -------------------------------------------------------------
    @app.route('/api/analyze', methods=['POST'])
    def analyze_resume():
        """
        Analyzes uploaded file (PDF/DOCX/TXT) or raw text.
        Extracts candidate data, skills, education, experience, scores, and feedback.
        """
        try:
            resume_text = ""
            filename = "pasted_resume.txt"

            # Check if file was uploaded
            if 'resume_file' in request.files:
                file = request.files['resume_file']
                if file and file.filename != '':
                    if not allowed_file(file.filename):
                        return jsonify({
                            "status": "error",
                            "message": f"Unsupported file extension. Allowed: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"
                        }), 400
                    
                    filename = secure_filename(file.filename)
                    # Extract directly from file stream / bytes
                    file_bytes = file.read()
                    resume_text = extract_text_from_file(file_bytes, filename=filename)

            # Check for JSON or form data raw text
            if not resume_text:
                if request.is_json:
                    resume_text = request.json.get('resume_text', '')
                else:
                    resume_text = request.form.get('resume_text', '')

            if not resume_text or len(resume_text.strip()) < 30:
                return jsonify({
                    "status": "error",
                    "message": "Unable to extract meaningful text. Please ensure the file contains readable text or paste your resume content."
                }), 400

            # 1. NLP Text Preprocessing
            cleaned_text = clean_text(resume_text, preserve_newlines=True)

            # 2. Information Extraction
            extractor = ResumeExtractor(cleaned_text)
            extracted_data = extractor.extract_all()
            extracted_data['raw_text'] = cleaned_text

            # 3. Scoring & ATS Evaluation
            scorer = ResumeScorer(extracted_data)
            score_data = scorer.calculate_score()

            # 4. Actionable Feedback & Verb Recommendations
            feedback_data = generate_feedback(extracted_data, score_data)

            # 5. Word Frequency (for word clouds & keyword highlights)
            word_frequencies = compute_word_frequencies(cleaned_text, top_n=20)

            # 6. Optional Job Description Match (if provided in same request)
            jd_text = ""
            if request.is_json:
                jd_text = request.json.get('jd_text', '')
            else:
                jd_text = request.form.get('jd_text', '')

            jd_match_data = None
            if jd_text and len(jd_text.strip()) > 30:
                matcher = JDMatcher(cleaned_text, jd_text)
                jd_match_data = matcher.match()

            response_payload = {
                "status": "success",
                "filename": filename,
                "extracted_data": extracted_data,
                "score": score_data,
                "feedback": feedback_data,
                "word_frequencies": word_frequencies,
                "jd_match": jd_match_data
            }

            return jsonify(response_payload)

        except Exception as e:
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }), 500

    @app.route('/api/match-jd', methods=['POST'])
    def match_job_description():
        """
        Compares resume text against a target job description.
        Returns match percentage, matching skills, and missing keywords.
        """
        try:
            resume_text = ""
            jd_text = ""

            # Check for file upload
            if 'resume_file' in request.files:
                file = request.files['resume_file']
                if file and file.filename != '':
                    file_bytes = file.read()
                    resume_text = extract_text_from_file(file_bytes, filename=file.filename)

            if not resume_text:
                if request.is_json:
                    resume_text = request.json.get('resume_text', '')
                else:
                    resume_text = request.form.get('resume_text', '')

            if request.is_json:
                jd_text = request.json.get('jd_text', '')
            else:
                jd_text = request.form.get('jd_text', '')

            if not resume_text or len(resume_text.strip()) < 30:
                return jsonify({"status": "error", "message": "Valid resume text is required."}), 400

            if not jd_text or len(jd_text.strip()) < 30:
                return jsonify({"status": "error", "message": "Valid job description text is required."}), 400

            matcher = JDMatcher(resume_text, jd_text)
            match_results = matcher.match()

            return jsonify({
                "status": "success",
                "match": match_results
            })

        except Exception as e:
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "ResumeIQ API",
            "version": "1.0.0"
        })

    # Error handlers
    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"status": "error", "message": "File size exceeds the 16 MB limit."}), 413

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({"status": "error", "message": "Endpoint not found"}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1')
    print(f"🚀 ResumeIQ running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
