"""
Job Description (JD) Matcher and ATS Simulator.
Computes semantic similarity (TF-IDF & Cosine Similarity) and skill gap analysis.
Includes pure-Python fallback for zero external dependency lock-in.
"""

import math
from collections import Counter
from .cleaner import tokenize_words
from .extractor import ResumeExtractor

class JDMatcher:
    def __init__(self, resume_text, jd_text):
        self.resume_text = resume_text or ""
        self.jd_text = jd_text or ""

    def match(self):
        """
        Executes full ATS matching:
        - Skill overlap analysis (matching, missing, extra)
        - Semantic text cosine similarity
        - Overall ATS fit score (0-100%)
        - Actionable optimization recommendations
        """
        resume_extractor = ResumeExtractor(self.resume_text)
        jd_extractor = ResumeExtractor(self.jd_text)

        resume_skills_dict = resume_extractor.extract_skills()
        jd_skills_dict = jd_extractor.extract_skills()

        resume_skills = set(resume_skills_dict.get('all', []))
        jd_skills = set(jd_skills_dict.get('all', []))

        # Skill overlap
        matching_skills = sorted(list(resume_skills.intersection(jd_skills)))
        missing_skills = sorted(list(jd_skills - resume_skills))
        extra_skills = sorted(list(resume_skills - jd_skills))

        # Skill match percentage
        if jd_skills:
            skill_match_pct = round((len(matching_skills) / len(jd_skills)) * 100, 1)
        else:
            skill_match_pct = 75.0 if matching_skills else 50.0

        # Semantic similarity
        cosine_sim_pct = self._calculate_cosine_similarity()

        # Weighted final match score: 60% skills + 40% semantic text
        final_score = round((0.60 * skill_match_pct) + (0.40 * cosine_sim_pct))
        final_score = max(0, min(100, final_score))

        verdict = self._get_verdict(final_score)
        tailoring_tips = self._generate_tailoring_tips(missing_skills, final_score)

        return {
            "match_score": final_score,
            "skill_match_score": skill_match_pct,
            "semantic_score": cosine_sim_pct,
            "verdict": verdict,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills[:15],
            "total_jd_skills": len(jd_skills),
            "tailoring_tips": tailoring_tips
        }

    def _calculate_cosine_similarity(self):
        """Calculates Cosine Similarity between resume and JD using TF-IDF."""
        # 1. Try scikit-learn
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([self.resume_text, self.jd_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Rescale similarity into an intuitive 0-100 range
            return round(float(sim) * 100, 1)
        except Exception:
            pass

        # 2. Pure-Python TF-IDF Cosine Similarity Fallback
        return self._pure_python_cosine_similarity()

    def _pure_python_cosine_similarity(self):
        """Fast pure-Python TF-IDF cosine similarity."""
        tokens_resume = tokenize_words(self.resume_text, lowercase=True, remove_stop=True)
        tokens_jd = tokenize_words(self.jd_text, lowercase=True, remove_stop=True)

        if not tokens_resume or not tokens_jd:
            return 0.0

        tf_r = Counter(tokens_resume)
        tf_jd = Counter(tokens_jd)

        # Vocabulary of words present in either
        all_words = set(tf_r.keys()).union(set(tf_jd.keys()))
        if not all_words:
            return 0.0

        # Term frequency vectors
        dot_product = sum(tf_r[w] * tf_jd[w] for w in all_words)
        norm_r = math.sqrt(sum(cnt ** 2 for cnt in tf_r.values()))
        norm_jd = math.sqrt(sum(cnt ** 2 for cnt in tf_jd.values()))

        if norm_r == 0 or norm_jd == 0:
            return 0.0

        sim = dot_product / (norm_r * norm_jd)
        return round(sim * 100, 1)

    def _get_verdict(self, score):
        """Returns ATS match verdict."""
        if score >= 85:
            return "Exceptional Match (Top 5% Candidate)"
        elif score >= 70:
            return "Strong Match (High Likelihood to Pass ATS)"
        elif score >= 55:
            return "Moderate Match (Consider Adding Missing Keywords)"
        elif score >= 40:
            return "Fair Match (Significant Keyword Gaps)"
        else:
            return "Low Match (Resume Needs Customization for this Role)"

    def _generate_tailoring_tips(self, missing_skills, score):
        """Generates specific guidance to help pass the ATS for this job."""
        tips = []
        if missing_skills:
            top_missing = ", ".join(missing_skills[:5])
            tips.append(f"Incorporate missing core skills if you have experience with them: {top_missing}.")

        if score < 70:
            tips.append("Mirror relevant phrases and terminology from the job description in your project bullet points.")
            tips.append("Ensure your job titles or professional summary highlight the primary role title mentioned in the JD.")
        else:
            tips.append("Your resume aligns well with this job posting! Emphasize your quantifiable achievements in interview prep.")

        tips.append("Maintain clean, single-column formatting so automated ATS parsers don't drop your key sections.")
        return tips
