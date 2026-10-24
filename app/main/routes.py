from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import select, func
from app.models import Resume, Analysis

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return render_template("index.html")

@main_bp.get("/dashboard")
@login_required
def dashboard():
    resumes = current_user.resumes
    analysis_count = 0
    scores = []
    for resume in resumes:
        analysis_count += len(resume.analyses)
        scores.extend([a.readiness_score for a in resume.analyses])
    latest_score = scores[-1] if scores else None
    return render_template(
        "dashboard.html",
        resumes=resumes,
        analysis_count=analysis_count,
        latest_score=latest_score,
    )
