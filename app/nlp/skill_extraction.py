import re

SKILL_ALIASES = {
    "python": "Python", "java": "Java", "javascript": "JavaScript",
    "typescript": "TypeScript", "c++": "C++", "c#": "C#",
    "flask": "Flask", "django": "Django", "react": "React",
    "react.js": "React", "node.js": "Node.js", "sql": "SQL",
    "postgresql": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB",
    "aws": "AWS", "azure": "Azure", "docker": "Docker",
    "kubernetes": "Kubernetes", "git": "Git", "html": "HTML",
    "css": "CSS", "machine learning": "Machine Learning",
    "natural language processing": "NLP", "nlp": "NLP",
    "rest api": "REST API", "rest apis": "REST API",
}

def extract_skills(text):
    found = set()
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"(?<![\w+#.])" + re.escape(alias) + r"(?![\w+#.])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.add(canonical)
    return sorted(found, key=str.casefold)
