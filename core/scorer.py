"""
Resume scoring algorithm and multi-dimensional ATS evaluation.
Calculates an aggregate score (0-100), sub-category ratings, and assigns letter grades.
"""

class ResumeScorer:
    def __init__(self, extracted_data):
        self.data = extracted_data
        self.contact = extracted_data.get('contact', {})
        self.skills = extracted_data.get('skills', {})
        self.education = extracted_data.get('education', [])
        self.experience = extracted_data.get('experience', {})
        self.projects = extracted_data.get('projects', [])
        self.certifications = extracted_data.get('certifications', [])
        self.metrics = extracted_data.get('metrics', {})
        self.word_count = extracted_data.get('raw_word_count', 0)

    def calculate_score(self):
        """Calculates total score, category breakdown, grade, and audit details."""
        breakdown = {
            "contact_score": self._score_contact(),          # max 10
            "skills_score": self._score_skills(),            # max 25
            "experience_score": self._score_experience(),    # max 25
            "education_score": self._score_education(),      # max 15
            "impact_score": self._score_impact(),            # max 15
            "formatting_score": self._score_formatting()     # max 10
        }

        total = sum(breakdown.values())
        total = max(0, min(100, round(total)))

        grade, grade_label = self._compute_grade(total)
        strengths, improvements = self._audit_points(breakdown)

        return {
            "total_score": total,
            "grade": grade,
            "grade_label": grade_label,
            "breakdown": breakdown,
            "strengths": strengths,
            "improvements": improvements
        }

    def _score_contact(self):
        """Scores candidate contact details (max 10 points)."""
        score = 0
        if self.contact.get('name') and self.contact['name'] != 'Candidate':
            score += 2
        if self.contact.get('email'):
            score += 2
        if self.contact.get('phone'):
            score += 2
        if self.contact.get('linkedin'):
            score += 2
        if self.contact.get('github') or self.contact.get('portfolio'):
            score += 2
        return min(10, score)

    def _score_skills(self):
        """Scores skills breadth, count, and multi-category diversity (max 25 points)."""
        score = 0
        total_skills = self.skills.get('total_count', 0)
        categories = self.skills.get('by_category', {})

        # Point allocation by quantity
        if total_skills >= 15:
            score += 15
        elif total_skills >= 10:
            score += 12
        elif total_skills >= 5:
            score += 8
        elif total_skills >= 1:
            score += 4

        # Category diversity (up to 10 points for 4+ distinct domains)
        cat_count = len(categories)
        if cat_count >= 5:
            score += 10
        elif cat_count >= 3:
            score += 7
        elif cat_count >= 1:
            score += 4

        return min(25, score)

    def _score_experience(self):
        """Scores work history and projects depth (max 25 points)."""
        score = 0
        roles = self.experience.get('roles_count', 0)
        years = self.experience.get('estimated_years', 0)
        projs = len(self.projects)

        # Experience roles or projects
        if roles >= 2:
            score += 14
        elif roles == 1:
            score += 9
        elif projs >= 2:
            score += 8

        # Project portfolio bonus
        if projs >= 3:
            score += 8
        elif projs >= 1:
            score += 5

        # Certifications bonus
        if len(self.certifications) >= 1:
            score += 3

        return min(25, score)

    def _score_education(self):
        """Scores degree, institution, and major detection (max 15 points)."""
        score = 0
        if self.education:
            score += 7  # degree present
            for ed in self.education:
                if ed.get('institution') and 'University / Institution' not in ed.get('institution', ''):
                    score += 4
                    break
            for ed in self.education:
                if ed.get('year'):
                    score += 2
                    break
                if ed.get('gpa'):
                    score += 2
                    break
        return min(15, score)

    def _score_impact(self):
        """Scores action verbs and quantifiable results (max 15 points)."""
        score = 0
        verbs = self.metrics.get('action_verbs_count', 0)
        results = self.metrics.get('quantifiable_results_count', 0)

        # Action verbs
        if verbs >= 8:
            score += 8
        elif verbs >= 4:
            score += 5
        elif verbs >= 1:
            score += 2

        # Quantifiable metrics (%, $, numbers)
        if results >= 4:
            score += 7
        elif results >= 2:
            score += 5
        elif results >= 1:
            score += 3

        return min(15, score)

    def _score_formatting(self):
        """Scores resume length and text density (max 10 points)."""
        score = 0
        # Optimal word count for 1-2 page resume: 350 to 900 words
        if 350 <= self.word_count <= 950:
            score += 7
        elif 200 <= self.word_count < 350:
            score += 4
        elif self.word_count > 950:
            score += 5
        else:
            score += 2

        # Bonus for presence of both skills and experience
        if self.skills.get('total_count', 0) > 0 and (self.experience.get('roles_count', 0) > 0 or len(self.projects) > 0):
            score += 3

        return min(10, score)

    def _compute_grade(self, total):
        """Maps numerical score to grade and descriptor."""
        if total >= 90:
            return "A+", "Exceptional - Ready for Elite Tech Roles"
        elif total >= 80:
            return "A", "Strong - High Interview Probability"
        elif total >= 70:
            return "B+", "Competitive - Minor Tweaks Recommended"
        elif total >= 60:
            return "B", "Average - Needs More Impact & Skills"
        elif total >= 50:
            return "C", "Below Average - Major Gaps Detected"
        else:
            return "Needs Work", "Critical Sections or Keywords Missing"

    def _audit_points(self, breakdown):
        """Provides dynamic strengths and actionable improvement bullets."""
        strengths = []
        improvements = []

        # Contact
        if breakdown['contact_score'] >= 8:
            strengths.append("Complete contact profile with professional links (LinkedIn/GitHub).")
        else:
            improvements.append("Add missing contact links (LinkedIn, GitHub, or Portfolio URL) to boost credibility.")

        # Skills
        if breakdown['skills_score'] >= 20:
            strengths.append(f"Rich technical skill diversity ({self.skills.get('total_count', 0)} skills identified).")
        elif breakdown['skills_score'] < 14:
            improvements.append("Expand your skills section with modern frameworks, tools, and cloud platforms.")

        # Experience & Projects
        if breakdown['experience_score'] >= 18:
            strengths.append("Demonstrated professional experience and well-defined technical projects.")
        else:
            improvements.append("Detail more project achievements with tech stacks and quantifiable outcomes.")

        # Impact & Verbs
        if breakdown['impact_score'] >= 11:
            strengths.append("Strong usage of action verbs and quantifiable impact metrics (%, $, scale).")
        else:
            improvements.append("Include more measurable metrics (e.g., 'reduced latency by 35%', 'scaled to 10k users').")

        # Word count
        if self.word_count < 300:
            improvements.append("Resume is somewhat brief (< 300 words). Elaborate on your technical contributions.")
        elif self.word_count > 1000:
            improvements.append("Resume exceeds 1,000 words. Try to keep it concise, ideally 1-2 pages.")

        return strengths, improvements
