"""
Information extraction engine for resumes.
Extracts contact details, skills, education, experience, certifications, and projects using NLP & heuristics.
"""

import re
from datetime import datetime
from .cleaner import clean_text, tokenize_words, extract_ngrams
from .skills_db import SKILL_CATEGORIES, SKILL_SYNONYMS, SKILL_TO_CATEGORY, ALL_SKILLS

class ResumeExtractor:
    def __init__(self, raw_text):
        self.raw_text = raw_text or ""
        self.cleaned_lines = [line.strip() for line in self.raw_text.splitlines() if line.strip()]
        self.text_lower = self.raw_text.lower()

    def extract_all(self):
        """Runs all extraction modules and returns a structured dictionary."""
        contact = self.extract_contact_info()
        skills = self.extract_skills()
        education = self.extract_education()
        experience = self.extract_experience()
        certifications = self.extract_certifications()
        projects = self.extract_projects()
        metrics = self.extract_metrics()

        return {
            "contact": contact,
            "skills": skills,
            "education": education,
            "experience": experience,
            "certifications": certifications,
            "projects": projects,
            "metrics": metrics,
            "raw_word_count": len(self.raw_text.split()),
            "raw_char_count": len(self.raw_text)
        }

    def extract_contact_info(self):
        """Extracts name, email, phone, links, and location."""
        return {
            "name": self._extract_name(),
            "email": self._extract_email(),
            "phone": self._extract_phone(),
            "linkedin": self._extract_linkedin(),
            "github": self._extract_github(),
            "portfolio": self._extract_portfolio(),
            "location": self._extract_location()
        }

    def _extract_name(self):
        """Extracts candidate name from the top section of the resume."""
        if not self.cleaned_lines:
            return "Candidate"

        # Check top 6 lines
        ignored_words = {
            'resume', 'curriculum', 'vitae', 'cv', 'contact', 'profile', 'summary',
            'page', 'email', 'phone', 'portfolio', 'github', 'linkedin', 'address',
            'developer', 'engineer', 'experience', 'education', 'skills', 'objective'
        }

        for line in self.cleaned_lines[:6]:
            # Remove symbols, extra whitespace
            candidate = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            words = candidate.split()

            # Name typically has 2 to 4 words
            if 2 <= len(words) <= 4:
                # Ensure no ignored words
                if not any(w.lower() in ignored_words for w in words):
                    # Ensure first letters are capitalized or title-cased
                    if all(len(w) > 1 and w[0].isupper() for w in words):
                        return candidate
                    # Or if line is all uppercase, convert to title case
                    if candidate.isupper():
                        return candidate.title()

        # Fallback: first non-empty line if short enough
        if self.cleaned_lines:
            first = re.sub(r'[^a-zA-Z\s]', '', self.cleaned_lines[0]).strip()
            if 1 < len(first.split()) <= 4:
                return first.title()

        return "Candidate"

    def _extract_email(self):
        """Extracts primary email address."""
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        matches = re.findall(email_pattern, self.raw_text)
        if matches:
            # Clean trailing dots
            email = matches[0].rstrip('.')
            return email.lower()
        return None

    def _extract_phone(self):
        """Extracts phone number supporting multiple global patterns."""
        phone_patterns = [
            r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
            r'(\+?\d{1,3}[\s-]?)?\d{10}',
            r'(\+91[\s-]?)?[6789]\d{9}'
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, self.raw_text)
            if matches:
                # Find full match span
                m = re.search(pattern, self.raw_text)
                if m:
                    return m.group(0).strip()
        return None

    def _extract_linkedin(self):
        """Extracts LinkedIn profile URL or handle."""
        match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)', self.raw_text, re.I)
        if match:
            return f"https://linkedin.com/in/{match.group(1)}"
        return None

    def _extract_github(self):
        """Extracts GitHub profile URL or handle."""
        match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)', self.raw_text, re.I)
        if match:
            # Avoid matching repo names if followed by common assets
            user = match.group(1)
            if user.lower() not in ('pulls', 'issues', 'features', 'pricing'):
                return f"https://github.com/{user}"
        return None

    def _extract_portfolio(self):
        """Extracts portfolio, personal website, or LeetCode URL."""
        urls = re.findall(r'https?:\/\/(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:\/[^\s)]*)?', self.raw_text)
        for u in urls:
            u_str = u[0] if isinstance(u, tuple) else u
            lower = u_str.lower()
            if not any(x in lower for x in ['linkedin.com', 'github.com', 'google.com', 'schema.org']):
                return f"https://{u_str}"
        return None

    def _extract_location(self):
        """Detects city/state or remote location mentions."""
        loc_patterns = [
            r'([A-Z][a-zA-Z]+(?:[\s-][A-Z][a-zA-Z]+)?),\s*([A-Z]{2}\b|[A-Z][a-zA-Z]+)',
            r'\b(Remote|Hybrid|On-site|New York|San Francisco|Seattle|Austin|London|Bangalore|Bengaluru|Hyderabad|Toronto|Berlin)\b'
        ]
        for pattern in loc_patterns:
            match = re.search(pattern, self.raw_text)
            if match:
                return match.group(0).strip()
        return None

    def extract_skills(self):
        """
        Extracts skills using 1-gram, 2-gram, 3-gram and 4-gram scanning against taxonomy.
        Returns categorized skills, all unique canonical skills, and top skill count.
        """
        found_skills = set()
        text_lower = f" {self.text_lower} "

        # Clean text into tokens
        tokens = tokenize_words(self.text_lower, lowercase=True, remove_stop=False)
        ngrams_2 = extract_ngrams(tokens, 2)
        ngrams_3 = extract_ngrams(tokens, 3)
        ngrams_4 = extract_ngrams(tokens, 4)

        all_candidate_phrases = set(tokens + ngrams_2 + ngrams_3 + ngrams_4)

        # 1. Match against ALL_SKILLS taxonomy
        for phrase in all_candidate_phrases:
            if phrase in ALL_SKILLS:
                canonical = SKILL_SYNONYMS.get(phrase, phrase.title())
                found_skills.add(canonical)

        # 2. Match special keywords with regex word boundaries (e.g. C++, C#, Go, R)
        special_checks = [
            (r'\bc\+\+\b', 'C++'),
            (r'\bc\#\b', 'C#'),
            (r'\b\.net(?:\s+core)?\b', '.NET Core'),
            (r'\bnode(?:\.js)?\b', 'Node.js'),
            (r'\breact(?:\.js)?\b', 'React'),
            (r'\bvue(?:\.js)?\b', 'Vue.js'),
            (r'\bnext(?:\.js)?\b', 'Next.js'),
            (r'\baws\b', 'Amazon Web Services (AWS)'),
            (r'\bgcp\b', 'Google Cloud Platform (GCP)'),
            (r'\bk8s\b', 'Kubernetes'),
            (r'\bci\/cd\b', 'CI/CD'),
            (r'\bnlp\b', 'Natural Language Processing (NLP)'),
            (r'\bllms?\b', 'Large Language Models (LLMs)'),
            (r'\brag\b', 'RAG (Retrieval-Augmented Generation)'),
            (r'\bgenai\b', 'Generative AI'),
            (r'\bml\b', 'Machine Learning'),
            (r'\bai\b', 'Artificial Intelligence (AI)')
        ]
        for pattern, canon in special_checks:
            if re.search(pattern, text_lower):
                found_skills.add(canon)

        # Categorize found skills
        categorized = {}
        for skill in found_skills:
            low = skill.lower()
            category = SKILL_TO_CATEGORY.get(low)
            if not category:
                # Check if it was canonicalized
                for k, v in SKILL_SYNONYMS.items():
                    if v.lower() == low or k == low:
                        category = SKILL_TO_CATEGORY.get(k)
                        break
            if not category:
                category = "Other Technical Skills"

            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill)

        # Sort within each category
        for cat in categorized:
            categorized[cat].sort()

        return {
            "all": sorted(list(found_skills)),
            "total_count": len(found_skills),
            "by_category": categorized
        }

    def extract_education(self):
        """Extracts degree, major, university, and graduation year."""
        education_records = []
        degree_patterns = [
            r'\b(Ph\.?D\.?|Doctor of Philosophy)\b',
            r'\b(Master of Science|Master of Technology|M\.?S\.?|M\.?Tech\.?|M\.?C\.?A\.?|MBA)\b',
            r'\b(Bachelor of Science|Bachelor of Technology|Bachelor of Engineering|B\.?S\.?|B\.?Tech\.?|B\.?E\.?|B\.?C\.?A\.?|B\.?A\.?)\b',
            r'\b(Bachelors?|Masters?|Associate|Diploma|High School)\b'
        ]

        major_patterns = [
            r'in\s+([A-Za-z\s]+(?:Computer Science|Data Science|Software Engineering|Information Technology|Electrical|Mechanical|Mathematics|Physics|AI))',
            r'\b(Computer Science|Data Science|Software Engineering|Information Technology|Electrical Engineering|Mechanical Engineering|Artificial Intelligence|Cybersecurity)\b'
        ]

        year_pattern = r'\b(19\d{2}|20\d{2})\s*(?:-|–|to)\s*(19\d{2}|20\d{2}|Present|Current)\b|\b(20\d{2})\b'
        gpa_pattern = r'\b(?:GPA|CGPA)[:\s]*([0-4]\.\d{1,2}(?:\s*\/\s*4(?:\.0)?)?|[0-9]\.\d{1,2}(?:\s*\/\s*10(?:\.0)?)?|\d{2,3}%)\b'

        lines = self.cleaned_lines
        for i, line in enumerate(lines):
            for deg_pat in degree_patterns:
                deg_match = re.search(deg_pat, line, re.I)
                if deg_match:
                    degree = deg_match.group(0).strip()
                    # Context lines around degree
                    context = " ".join(lines[max(0, i-1):min(len(lines), i+3)])

                    # Major
                    major = None
                    for maj_pat in major_patterns:
                        m_match = re.search(maj_pat, context, re.I)
                        if m_match:
                            major = m_match.group(1).strip()
                            break

                    # Year
                    year = None
                    y_match = re.search(year_pattern, context)
                    if y_match:
                        year = y_match.group(0).strip()

                    # GPA
                    gpa = None
                    g_match = re.search(gpa_pattern, context, re.I)
                    if g_match:
                        gpa = g_match.group(0).strip()

                    # University detection heuristic
                    uni = self._find_university(context)

                    record = {
                        "degree": degree,
                        "major": major or "Computer Science / Related Field",
                        "institution": uni,
                        "year": year,
                        "gpa": gpa,
                        "raw_line": line
                    }

                    # Avoid duplicate records
                    if not any(r['degree'].lower() == degree.lower() and r['year'] == year for r in education_records):
                        education_records.append(record)
                    break

        return education_records

    def _find_university(self, text):
        """Finds university or college name in text snippet."""
        uni_patterns = [
            r'([A-Z][a-zA-Z\s]+(?:University|Institute|College|Academy|School of Technology|Polytechnic))',
            r'\b(MIT|Stanford|Harvard|UC Berkeley|Carnegie Mellon|Oxford|Cambridge|IIT|NIT|BITS)\b'
        ]
        for pat in uni_patterns:
            m = re.search(pat, text)
            if m:
                return m.group(0).strip()
        return "University / Institution"

    def extract_experience(self):
        """
        Extracts work experience: job titles, companies, dates, and calculates total experience.
        """
        title_keywords = [
            r'Software Engineer', r'Senior Software Engineer', r'Full Stack Developer',
            r'Frontend Developer', r'Backend Developer', r'Data Scientist',
            r'Machine Learning Engineer', r'AI Engineer', r'DevOps Engineer',
            r'Cloud Architect', r'System Architect', r'Product Manager',
            r'Project Manager', r'Tech Lead', r'Engineering Manager',
            r'Intern', r'Research Assistant', r'Data Analyst', r'QA Engineer'
        ]
        pattern = r'\b(' + '|'.join(title_keywords) + r')\b'

        experience_list = []
        lines = self.cleaned_lines

        # Regex for date ranges (e.g. "Jan 2021 - Present" or "2019 - 2022")
        date_range_regex = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4})\s*(?:-|–|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}|Present|Current)'

        total_months = 0
        current_year = datetime.now().year

        for i, line in enumerate(lines):
            match = re.search(pattern, line, re.I)
            if match:
                title = match.group(0)
                context_block = lines[max(0, i):min(len(lines), i+5)]
                joined_block = " ".join(context_block)

                # Look for date in current or adjacent lines
                dates = re.search(date_range_regex, joined_block, re.I)
                date_str = dates.group(0) if dates else "Not specified"

                # Estimate company from the same line or next line
                comp_line = line.replace(title, '').strip(' -|,')
                company = comp_line if len(comp_line) > 2 else (lines[i+1] if i+1 < len(lines) else "Technology Company")
                # Clean up company text
                company = re.sub(r'\(.*?\)', '', company).strip(' -|,')

                # Collect bullet points (lines starting with •, -, *, or numbered)
                bullets = []
                for k in range(i+1, min(len(lines), i+8)):
                    subline = lines[k].strip()
                    if re.match(r'^[•\-\*\d\.]', subline) or len(subline.split()) > 6:
                        bullets.append(subline.lstrip('•-* 0123456789.'))
                    elif any(re.search(pattern, subline, re.I) for p in [pattern]):
                        break

                experience_list.append({
                    "title": title.title(),
                    "company": company.title() if company else "Company",
                    "duration": date_str,
                    "highlights": bullets[:4]
                })

        # Calculate estimated total years of experience
        years_found = re.findall(r'\b(20\d{2}|19\d{2})\b', self.raw_text)
        if years_found:
            years = sorted([int(y) for y in years_found if int(y) <= current_year])
            if len(years) >= 2:
                estimated_years = max(0, min(25, years[-1] - years[0]))
            else:
                estimated_years = 1 if len(experience_list) > 0 else 0
        else:
            estimated_years = len(experience_list) * 2

        return {
            "history": experience_list,
            "estimated_years": estimated_years,
            "roles_count": len(experience_list)
        }

    def extract_certifications(self):
        """Extracts recognizable certifications and credentials."""
        cert_patterns = [
            r'AWS Certified\s*[A-Za-z\s]+',
            r'Google Cloud Certified\s*[A-Za-z\s]+',
            r'Microsoft Certified:\s*[A-Za-z\s]+',
            r'Certified Kubernetes Administrator\s*\(?CKA\)?',
            r'Certified Kubernetes Application Developer\s*\(?CKAD\)?',
            r'Project Management Professional\s*\(?PMP\)?',
            r'CompTIA\s+[A-Za-z\+]+',
            r'Cisco Certified\s*[A-Za-z\s]+',
            r'DeepLearning\.AI\s+[A-Za-z\s]+',
            r'Coursera\s+[A-Za-z\s]+Certificate',
            r'Meta\s+[A-Za-z\s]+Professional Certificate'
        ]

        found = []
        for pat in cert_patterns:
            matches = re.findall(pat, self.raw_text, re.I)
            for m in matches:
                clean_cert = re.sub(r'\s+', ' ', m).strip()
                if clean_cert and clean_cert not in found:
                    found.append(clean_cert)

        # Fallback: check lines under a "Certifications" heading
        if not found:
            in_cert_section = False
            for line in self.cleaned_lines:
                if re.match(r'^(certifications?|licenses?|credentials)\b', line, re.I):
                    in_cert_section = True
                    continue
                if in_cert_section:
                    if re.match(r'^(education|skills|experience|projects|publications)\b', line, re.I):
                        break
                    if len(line.split()) < 12 and len(line) > 5:
                        found.append(line.strip(' •-*'))

        return found[:8]

    def extract_projects(self):
        """Extracts key personal/academic projects and their descriptions."""
        projects = []
        in_proj_section = False
        current_project = None

        for line in self.cleaned_lines:
            # Section header
            if re.match(r'^(projects?|personal projects?|academic projects?)\b', line, re.I):
                in_proj_section = True
                continue

            if in_proj_section:
                # Stop if hitting another major section
                if re.match(r'^(experience|education|skills|certifications|awards|summary)\b', line, re.I):
                    break

                # Project title line: usually short, may have '|' or ':'
                if ('|' in line or ':' in line or len(line.split()) <= 6) and not line.startswith(('•', '-', '*')):
                    if current_project:
                        projects.append(current_project)
                    parts = re.split(r'[:|]', line)
                    current_project = {
                        "name": parts[0].strip(' •-*'),
                        "tech_stack": parts[1].strip() if len(parts) > 1 else "",
                        "details": []
                    }
                elif current_project and (line.startswith(('•', '-', '*')) or len(line.split()) > 5):
                    current_project["details"].append(line.lstrip(' •-*'))

        if current_project:
            projects.append(current_project)

        return projects[:6]

    def extract_metrics(self):
        """
        Analyzes action verbs and quantifiable impact (%, $, numbers) in the resume.
        """
        strong_verbs = [
            "accelerated", "achieved", "architected", "automated", "built", "spearheaded",
            "engineered", "deployed", "designed", "developed", "increased", "reduced",
            "optimized", "orchestrated", "transformed", "implemented", "scaled", "delivered",
            "resolved", "maximized", "minimized", "pioneered", "mentored", "negotiated"
        ]

        text_words = tokenize_words(self.text_lower)
        verbs_found = [v for v in strong_verbs if v in text_words]

        # Quantifiable impact pattern: e.g. 40%, $100k, 10x, 500+ users, 99.9% uptime
        impact_patterns = [
            r'\b\d+(?:\.\d+)?%',
            r'\$\d+(?:,\d{3})*(?:\.\d+)?[kmbKMB]?',
            r'\b\d+x\b',
            r'\b\d+\+\s*(?:users|clients|customers|requests|queries|tps|qps|endpoints|projects)\b'
        ]
        impact_matches = []
        for pat in impact_patterns:
            matches = re.findall(pat, self.raw_text, re.I)
            impact_matches.extend(matches)

        return {
            "action_verbs_count": len(verbs_found),
            "action_verbs": sorted(list(set(verbs_found))),
            "quantifiable_results_count": len(impact_matches),
            "quantifiable_results": list(set(impact_matches))[:10]
        }
