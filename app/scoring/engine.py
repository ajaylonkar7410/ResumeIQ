from app.nlp.skill_extraction import extract_skills

def analyze_resume(text):
    skills = extract_skills(text)
    lower = text.lower()
    checks = {
        "Contact information": bool("@" in text),
        "Education section": any(x in lower for x in ["education", "b.tech", "bachelor", "degree", "university"]),
        "Skills section or technical skills": bool(skills),
        "Projects or experience": any(x in lower for x in ["project", "experience", "internship", "employment"]),
        "Certifications or achievements": any(x in lower for x in ["certification", "certifications", "achievement", "award"]),
    }
    score = round(sum(checks.values()) / len(checks) * 100)
    suggestions = []
    if not checks["Contact information"]:
        suggestions.append("Add professional contact information, including an email address.")
    if not checks["Education section"]:
        suggestions.append("Add a clearly labeled education section.")
    if not checks["Skills section or technical skills"]:
        suggestions.append("Add a relevant skills section using skills you can substantiate.")
    if not checks["Projects or experience"]:
        suggestions.append("Describe relevant projects, internships, or work experience.")
    if not checks["Certifications or achievements"]:
        suggestions.append("Consider adding relevant certifications or measurable achievements.")
    if len(text.split()) < 100:
        suggestions.append("The extracted text is short; check whether the entire resume was parsed.")
    return {
        "readiness_score": score,
        "skills": skills,
        "checks": checks,
        "suggestions": suggestions,
        "disclaimer": "Illustrative rule-based readiness score; not an official ATS score or hiring prediction."
    }
