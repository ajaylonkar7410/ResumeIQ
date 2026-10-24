from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Resume
from app.nlp.skill_extraction import extract_skills

matching_bp = Blueprint("matching", __name__)

@matching_bp.route("/match", methods=["GET", "POST"])
@login_required
def match():
    result = None
    resumes = current_user.resumes
    if request.method == "POST":
        try:
            resume_id = int(request.form.get("resume_id", ""))
        except ValueError:
            resume_id = -1
        resume = next((r for r in resumes if r.id == resume_id), None)
        job_text = request.form.get("job_description", "").strip()
        if resume and job_text:
            resume_skills = set(extract_skills(resume.extracted_text))
            job_skills = set(extract_skills(job_text))
            matched = sorted(resume_skills & job_skills)
            missing = sorted(job_skills - resume_skills)
            denominator = len(job_skills)
            coverage = round(len(matched) / denominator * 100) if denominator else 0
            result = {
                "matched": matched,
                "missing": missing,
                "coverage": coverage,
                "note": "Keyword coverage is based on the starter skill dictionary. Missing means not found in the resume text, not that you lack the skill."
            }
        else:
            result = {"error": "Select one of your resumes and enter a job description."}
    return render_template("job_matching.html", resumes=resumes, result=result)
