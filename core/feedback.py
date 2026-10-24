"""
AI Feedback and Optimization Advisor.
Generates actionable recommendations, action verb improvements, and ATS formatting guidance.
"""

import re

WEAK_VERBS = [
    "worked on", "helped", "responsible for", "assisted", "handled",
    "participated in", "attempted", "tried", "did", "made"
]

STRONG_VERB_ALTERNATIVES = {
    "worked on": ["Engineered", "Developed", "Architected", "Spearheaded", "Executed"],
    "helped": ["Collaborated", "Facilitated", "Accelerated", "Supported"],
    "responsible for": ["Led", "Managed", "Directed", "Owned", "Delivered"],
    "assisted": ["Co-authored", "Bolstered", "Streamlined", "Contributed to"],
    "handled": ["Orchestrated", "Resolved", "Administered", "Governed"],
    "participated in": ["Contributed", "Engaged", "Collaborated", "Implemented"],
    "did": ["Executed", "Accomplished", "Produced", "Completed"],
    "made": ["Designed", "Formulated", "Built", "Constructed"]
}

def generate_feedback(extracted_data, score_data):
    """
    Produces structured, prioritized feedback for the candidate.
    """
    feedback_items = []
    text_lower = (extracted_data.get('raw_text') or "").lower()

    # 1. Weak verb analysis
    weak_found = []
    for weak in WEAK_VERBS:
        if weak in text_lower:
            alts = STRONG_VERB_ALTERNATIVES.get(weak, ["Engineered", "Implemented"])
            weak_found.append({
                "phrase": weak,
                "alternatives": alts
            })

    if weak_found:
        feedback_items.append({
            "category": "Impact & Action Verbs",
            "priority": "High",
            "title": "Replace Passive Language with High-Impact Action Verbs",
            "description": f"Found passive phrases like '{weak_found[0]['phrase']}'. Power verbs grab recruiter attention and convey direct ownership.",
            "examples": weak_found[:3]
        })

    # 2. Contact details feedback
    contact = extracted_data.get('contact', {})
    if not contact.get('linkedin'):
        feedback_items.append({
            "category": "Contact Profile",
            "priority": "Medium",
            "title": "Include Your LinkedIn Profile Link",
            "description": "Recruiters and ATS platforms look for your LinkedIn profile to cross-verify career history and network recommendations."
        })
    if not contact.get('github') and not contact.get('portfolio'):
        feedback_items.append({
            "category": "Contact Profile",
            "priority": "Medium",
            "title": "Add a GitHub or Portfolio URL",
            "description": "For technical candidates, direct links to code repositories or live demo sites significantly boost interview call-back rates."
        })

    # 3. Quantifiable impact feedback
    metrics = extracted_data.get('metrics', {})
    results_count = metrics.get('quantifiable_results_count', 0)
    if results_count < 3:
        feedback_items.append({
            "category": "Quantifiable Achievements",
            "priority": "High",
            "title": "Add Numbers, Metrics, and Business Impact",
            "description": "Recruiters look for the Google XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. Example: 'Reduced API response times by 40% by implementing Redis caching.'",
        })

    # 4. Skills depth feedback
    skills = extracted_data.get('skills', {})
    if skills.get('total_count', 0) < 12:
        feedback_items.append({
            "category": "Skills Breadth",
            "priority": "High",
            "title": "Expand Core Technical Skills",
            "description": "Modern ATS filters search for exact skill matches. Group your skills into categorized lists (e.g., Languages, Frameworks, Cloud, Databases)."
        })

    # 5. Experience / Projects feedback
    exp = extracted_data.get('experience', {})
    projects = extracted_data.get('projects', [])
    if exp.get('roles_count', 0) == 0 and len(projects) == 0:
        feedback_items.append({
            "category": "Experience & Projects",
            "priority": "High",
            "title": "Structure Your Work Experience or Technical Projects",
            "description": "Make sure your experience and project sections have distinct job titles/names, organizations, dates, and bulleted achievements."
        })

    # 6. Formatting & Length
    word_count = extracted_data.get('raw_word_count', 0)
    if word_count < 250:
        feedback_items.append({
            "category": "Content Depth",
            "priority": "Medium",
            "title": "Flesh Out Your Descriptions",
            "description": "Your resume has under 250 words. Aim for 400-800 words to sufficiently cover your achievements and pass ATS keyword thresholds."
        })
    elif word_count > 1000:
        feedback_items.append({
            "category": "Length & Brevity",
            "priority": "Low",
            "title": "Streamline Your Resume to 1-2 Pages",
            "description": "Recruiters spend an average of 6 seconds reviewing a resume. Trim repetitive bullet points to keep your resume punchy and scannable."
        })

    return {
        "items": feedback_items,
        "weak_verbs_detected": weak_found,
        "total_recommendations": len(feedback_items)
    }
