# ResumeIQ 🧠📄
### AI-Powered Resume Analysis & ATS Optimization Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

> **ResumeIQ** is a full-stack, production-ready AI resume parsing and analysis platform. It automatically processes uploaded resumes (PDF, DOCX, TXT), extracts candidate entities (skills, education, work experience, certifications, and contact details) using Natural Language Processing (NLP), evaluates ATS compatibility on a 0–100 scale, and benchmarks resumes against target job descriptions using TF-IDF and Cosine Similarity.

---

## 🌟 Key Highlights & Features

- **Multi-Format Document Parsing**: High-fidelity text extraction supporting `.pdf` (via `pdfplumber` and `pypdf`), `.docx` (via `python-docx` and XML stream fallbacks), and `.txt`.
- **Custom NLP Preprocessing Pipeline**: Built-in word and sentence tokenization, whitespace normalization, punctuation stripping, and stopwords filtering preserving critical tech tokens (e.g., `C++`, `C#`, `.NET`, `Node.js`, `CI/CD`).
- **1,200+ Curated Skill Taxonomy**: Broad multi-domain coverage across Programming Languages, Frontend, Backend, AI/Data Science, Cloud/DevOps, Databases, Testing, Cybersecurity, and Soft Skills with canonical synonym normalization.
- **Intelligent Information Extraction**:
  - Candidate details: Name, Email, Phone, LinkedIn, GitHub, and Portfolio URLs.
  - Work history: Job titles, organizations, duration, and bullet points.
  - Education: Degrees, majors, universities, graduation years, and GPA.
  - Professional certifications & credentials.
  - Quantifiable metrics (`%`, `$`, scale numbers) and strong action verbs vs. passive language detection.
- **Multi-Factor ATS Readiness Score (0–100)**: Transparent grading across Contact Completeness (10%), Skills Breadth (25%), Work History & Projects (25%), Education (15%), Quantifiable Impact (15%), and Content Density (10%).
- **Interactive Job Description (JD) Benchmark**: Direct ATS simulation vectorizing resumes and target job postings using TF-IDF and Cosine Similarity to reveal matching qualifications and missing keywords.
- **Export & Actionable Advice**: Instant printable PDF summary, raw JSON export, and prioritized recommendations (High/Medium/Low).

---

## 🏗️ Architecture & NLP Pipeline

```
  [ Upload: PDF / DOCX / TXT ]
               │
               ▼
┌──────────────────────────────┐
│   Multi-Engine Text Parser   │  (pdfplumber / pypdf / python-docx / fallback)
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Preprocessing & Cleaning    │  (Regex normalization, tokenization, tech-token preservation)
└──────────────┬───────────────┘
               │
               ├─────────────────────────────────────────┐
               ▼                                         ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│ Information Extractor        │          │   Scikit-Learn / TF-IDF      │
│ • Contact & Professional URL │          │   Job Description Matcher    │
│ • 1,200+ Categorized Skills  │          │   • Cosine Similarity (0-100)│
│ • Experience & Timeline      │          │   • Missing Keyword Gaps     │
│ • Degrees & Certifications   │          └──────────────┬───────────────┘
│ • Action Verbs & Metrics     │                         │
└──────────────┬───────────────┘                         │
               │                                         │
               ▼                                         ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│   ATS Scoring Engine (0-100) │◄─────────┤     AI Feedback Advisor      │
│   • Multi-Factor Audit       │          │     • Strong Verb Rewrites   │
│   • Grade A+ to Needs Work   │          │     • Formatting Guidelines  │
└──────────────┬───────────────┘          └──────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Interactive Web UI / API   │  (Dashboard, Skill Badges, PDF Report, JSON API)
└──────────────────────────────┘
```

---

## 📂 Project Structure

```
ResumeIQ/
├── app.py                      # Flask Application controller & REST endpoints
├── config.py                   # Central configuration
├── requirements.txt            # Python dependencies
├── Procfile                    # Render / Heroku deployment process
├── runtime.txt                 # Python runtime version
├── Dockerfile                  # Containerization setup
├── render.yaml                 # Render 1-click blueprint
├── vercel.json                 # Vercel serverless configuration
├── core/
│   ├── __init__.py             # Core package initializer
│   ├── parser.py               # PDF/DOCX/TXT multi-engine parser
│   ├── cleaner.py              # NLP cleaning, tokenization, n-grams
│   ├── extractor.py            # Entity extraction (Contact, Skills, Edu, Exp)
│   ├── skills_db.py            # 1,200+ skill taxonomy with canonical synonyms
│   ├── scorer.py               # 0-100 ATS scoring algorithm
│   ├── jd_matcher.py           # TF-IDF & Cosine Similarity JD matcher
│   └── feedback.py             # Action verb suggestions & ATS feedback
├── static/
│   ├── css/
│   │   └── style.css           # Modern glassmorphism UI & responsive styles
│   ├── js/
│   │   └── main.js             # Drag-and-drop upload, AJAX, dynamic DOM rendering
│   └── sample_resumes/
│       ├── software_engineer.txt # Sample Tech / SWE resume
│       └── data_scientist.txt    # Sample AI / Data Science resume
├── templates/
│   ├── base.html               # Shared layout, navbar, dark/light theme
│   ├── index.html              # Main interactive analyzer dashboard
│   ├── jd_match.html           # Dedicated side-by-side ATS matcher
│   ├── about.html              # Architecture & API documentation
│   └── 404.html                # Error page
└── uploads/
    └── .gitkeep                # Temporary upload buffer
```

---

## 🚀 Quickstart: Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ResumeIQ.git
cd ResumeIQ
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set a secret key
Set a unique random secret key in your environment before running the app. For example:

```powershell
# Windows PowerShell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

```bash
# macOS / Linux
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

For deployment, configure `SECRET_KEY` in your hosting provider's environment settings. Do not commit a real secret to Git.

### 5. Run the application
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser to access the dashboard!

---

## 🐳 Docker Setup

Run ResumeIQ anywhere inside an isolated container:

```bash
# Build the Docker image
docker build -t resumeiq:latest .

# Run the container on port 5000
docker run -d -p 5000:5000 --name resumeiq-app resumeiq:latest
```
Visit `http://localhost:5000`.

---

## ☁️ Deployment Guide (Live Site)

### Option 1: Deploy to Render (Recommended - Free Tier)
1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: initial ResumeIQ release"
   git remote add origin https://github.com/<your-username>/ResumeIQ.git
   git push -u origin main
   ```
2. Log into [Render.com](https://render.com).
3. Click **New +** &rarr; **Web Service**.
4. Connect your **ResumeIQ** GitHub repository.
5. Set:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4`
6. Click **Deploy Web Service**. Your live site URL will be ready in 1-2 minutes!

### Option 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app).
2. Click **New Project** &rarr; **Deploy from GitHub repo**.
3. Select `ResumeIQ`. Railway automatically reads the `Procfile` and `requirements.txt` and deploys your service.

---

## 📡 API Reference

### 1. Analyze Resume (`POST /api/analyze`)
Upload a file (`.pdf`, `.docx`, `.txt`) or pass raw text:

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -F "resume_file=@sample_resume.pdf" \
  -F "jd_text=Optional job description..."
```

**Response Format:**
```json
{
  "status": "success",
  "filename": "sample_resume.pdf",
  "extracted_data": {
    "contact": {
      "name": "Alexander Chen",
      "email": "alex.chen.dev@gmail.com",
      "phone": "+1 (415) 555-0192",
      "linkedin": "https://linkedin.com/in/alexchen-tech",
      "github": "https://github.com/alexchen-dev"
    },
    "skills": {
      "total_count": 28,
      "by_category": {
        "Programming Languages": ["Go", "Python", "TypeScript"],
        "Backend & APIs": ["Docker", "FastAPI", "Flask", "PostgreSQL", "Redis"]
      }
    },
    "experience": {
      "estimated_years": 5,
      "roles_count": 2
    }
  },
  "score": {
    "total_score": 92,
    "grade": "A+",
    "grade_label": "Exceptional - Ready for Elite Tech Roles",
    "breakdown": {
      "skills_score": 25,
      "experience_score": 24,
      "education_score": 14,
      "impact_score": 15,
      "contact_score": 10,
      "formatting_score": 9
    }
  }
}
```

### 2. ATS Job Match (`POST /api/match-jd`)
Compare resume text directly against a job description:

```bash
curl -X POST http://127.0.0.1:5000/api/match-jd \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Experienced Python engineer with Flask, PostgreSQL, and Docker...",
    "jd_text": "Looking for Senior Python Developer with Docker, AWS, and Kubernetes..."
  }'
```

---

## 📄 License
This project is open-source and distributed under the [MIT License](LICENSE).
