import json
import secrets
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Resume, Analysis
from app.resumes.parser import extract_text, ALLOWED_EXTENSIONS
from app.scoring.engine import analyze_resume

resumes_bp = Blueprint("resumes", __name__)

@resumes_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or not file.filename:
            flash("Choose a resume file first.", "error")
            return render_template("upload_resume.html")
        original = secure_filename(file.filename)
        suffix = Path(original).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            flash("Only PDF, DOCX, and TXT files are supported.", "error")
            return render_template("upload_resume.html")
        stored = secrets.token_hex(16) + suffix
        target = Path(current_app.config["UPLOAD_FOLDER"]) / stored
        file.save(target)
        try:
            text = extract_text(target)
            if not text:
                target.unlink(missing_ok=True)
                flash("No readable text was found. Scanned PDFs may require OCR.", "error")
                return render_template("upload_resume.html")
        except Exception:
            target.unlink(missing_ok=True)
            flash("The file could not be read. Check that it is a valid, unprotected document.", "error")
            return render_template("upload_resume.html")
        resume = Resume(
            user_id=current_user.id,
            original_filename=original,
            stored_filename=stored,
            extracted_text=text,
        )
        db.session.add(resume)
        db.session.flush()
        result = analyze_resume(text)
        analysis = Analysis(
            resume_id=resume.id,
            readiness_score=result["readiness_score"],
            skills_json=json.dumps(result["skills"]),
            suggestions_json=json.dumps(result["suggestions"]),
        )
        db.session.add(analysis)
        db.session.commit()
        flash("Resume uploaded and analyzed.", "success")
        return redirect(url_for("resumes.view_resume", resume_id=resume.id))
    return render_template("upload_resume.html")

@resumes_bp.get("/resume/<int:resume_id>")
@login_required
def view_resume(resume_id):
    resume = db.session.get(Resume, resume_id)
    if not resume or resume.user_id != current_user.id:
        abort(404)
    analysis = resume.analyses[-1] if resume.analyses else None
    return render_template("resume_detail.html", resume=resume, analysis=analysis)

@resumes_bp.post("/resume/<int:resume_id>/delete")
@login_required
def delete_resume(resume_id):
    resume = db.session.get(Resume, resume_id)
    if not resume or resume.user_id != current_user.id:
        abort(404)
    target = Path(current_app.config["UPLOAD_FOLDER"]) / resume.stored_filename
    target.unlink(missing_ok=True)
    db.session.delete(resume)
    db.session.commit()
    flash("Resume and associated analysis records deleted.", "success")
    return redirect(url_for("main.dashboard"))
