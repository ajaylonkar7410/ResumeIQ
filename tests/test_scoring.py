from app.scoring.engine import analyze_resume

def test_analyze_resume_finds_skills_and_returns_bounded_score():
    result = analyze_resume(
        "Contact: person@example.com\nEducation: B.Tech\nSkills: Python, Flask, SQL\n"
        "Projects: Developed a Flask project with Python and SQL. " * 3
    )
    assert 0 <= result["readiness_score"] <= 100
    assert "Python" in result["skills"]
    assert "Flask" in result["skills"]

def test_empty_text_returns_suggestions():
    result = analyze_resume("")
    assert result["readiness_score"] == 0
    assert result["suggestions"]
