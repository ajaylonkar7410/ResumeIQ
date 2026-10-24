/**
 * ResumeIQ - Frontend Application Logic
 * Manages theme, drag-and-drop uploads, API requests, animations, and dynamic dashboard rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Current analysis result cache
    let currentAnalysisData = null;

    // -------------------------------------------------------------
    // 1. THEME TOGGLE (Dark / Light)
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('resumeiq-theme') || 'theme-dark';
    document.body.className = savedTheme;
    updateThemeIcon(savedTheme);

    themeToggleBtn?.addEventListener('click', () => {
        const isDark = document.body.classList.contains('theme-dark');
        const newTheme = isDark ? 'theme-light' : 'theme-dark';
        document.body.className = newTheme;
        localStorage.setItem('resumeiq-theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        themeToggleBtn.innerHTML = theme === 'theme-light' 
            ? '<i class="fa-solid fa-moon"></i>' 
            : '<i class="fa-solid fa-sun"></i>';
    }

    // -------------------------------------------------------------
    // 2. TAB CONTROLS (Upload vs Paste)
    // -------------------------------------------------------------
    const tabUploadBtn = document.getElementById('tabUploadBtn');
    const tabPasteBtn = document.getElementById('tabPasteBtn');
    const uploadTab = document.getElementById('uploadTab');
    const pasteTab = document.getElementById('pasteTab');

    tabUploadBtn?.addEventListener('click', () => {
        tabUploadBtn.classList.add('active');
        tabPasteBtn.classList.remove('active');
        uploadTab.style.display = 'block';
        pasteTab.style.display = 'none';
    });

    tabPasteBtn?.addEventListener('click', () => {
        tabPasteBtn.classList.add('active');
        tabUploadBtn.classList.remove('active');
        pasteTab.style.display = 'block';
        uploadTab.style.display = 'none';
    });

    // -------------------------------------------------------------
    // 3. DRAG & DROP FILE UPLOAD
    // -------------------------------------------------------------
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeFileInput');
    const selectedFileInfo = document.getElementById('selectedFileInfo');
    const selectedFileName = document.getElementById('selectedFileName');
    const removeFileBtn = document.getElementById('removeFileBtn');

    if (dropZone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('drag-over');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                displaySelectedFile(files[0].name);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                displaySelectedFile(fileInput.files[0].name);
            }
        });

        removeFileBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.value = '';
            selectedFileInfo.style.display = 'none';
        });
    }

    function displaySelectedFile(name) {
        selectedFileName.innerText = name;
        selectedFileInfo.style.display = 'inline-flex';
    }

    // -------------------------------------------------------------
    // 4. TEXTAREA CONTROLS & CHAR COUNTER
    // -------------------------------------------------------------
    const resumeTextarea = document.getElementById('resumeTextarea');
    const charCount = document.getElementById('charCount');
    const clearTextBtn = document.getElementById('clearTextBtn');

    resumeTextarea?.addEventListener('input', () => {
        const len = resumeTextarea.value.length;
        charCount.innerText = `${len.toLocaleString()} characters`;
    });

    clearTextBtn?.addEventListener('click', () => {
        resumeTextarea.value = '';
        charCount.innerText = '0 characters';
    });

    // -------------------------------------------------------------
    // 5. JOB DESCRIPTION ACCORDION TOGGLE
    // -------------------------------------------------------------
    const toggleJdBtn = document.getElementById('toggleJdBtn');
    const jdBody = document.getElementById('jdBody');
    const jdArrow = document.getElementById('jdArrow');

    toggleJdBtn?.addEventListener('click', () => {
        const isHidden = jdBody.style.display === 'none' || jdBody.style.display === '';
        jdBody.style.display = isHidden ? 'block' : 'none';
        jdArrow.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
    });

    // -------------------------------------------------------------
    // 6. SAMPLE RESUME LOADERS
    // -------------------------------------------------------------
    const loadSweBtn = document.getElementById('loadSweSample');
    const loadDsBtn = document.getElementById('loadDsSample');

    loadSweBtn?.addEventListener('click', () => loadSample('swe'));
    loadDsBtn?.addEventListener('click', () => loadSample('data-scientist'));

    async function loadSample(role) {
        try {
            const res = await fetch(`/sample/${role}`);
            const data = await res.json();
            if (data.status === 'success') {
                // Switch to paste tab and populate textarea
                tabPasteBtn.click();
                resumeTextarea.value = data.text;
                charCount.innerText = `${data.text.length.toLocaleString()} characters`;
                // Clear any file input
                if (fileInput) fileInput.value = '';
                if (selectedFileInfo) selectedFileInfo.style.display = 'none';
                // Smooth scroll to submit
                document.getElementById('submitBtn')?.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (err) {
            alert('Failed to load sample resume.');
            console.error(err);
        }
    }

    // -------------------------------------------------------------
    // 7. FORM SUBMISSION & ANALYSIS
    // -------------------------------------------------------------
    const resumeForm = document.getElementById('resumeForm');
    const loadingCard = document.getElementById('loadingCard');
    const resultsDashboard = document.getElementById('resultsDashboard');
    const inputCard = document.getElementById('inputCard');
    const loadingStatusText = document.getElementById('loadingStatusText');

    resumeForm?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const hasFile = fileInput && fileInput.files.length > 0;
        const rawText = resumeTextarea ? resumeTextarea.value.trim() : '';
        const jdText = document.getElementById('jdTextarea')?.value.trim() || '';

        if (!hasFile && rawText.length < 30) {
            alert('Please select a resume file (PDF, DOCX, TXT) or paste your resume text (at least 30 characters).');
            return;
        }

        // Show loading state
        inputCard.style.display = 'none';
        loadingCard.style.display = 'block';
        resultsDashboard.style.display = 'none';

        // Animate loading text steps
        const steps = [
            "Parsing Document Structure...",
            "Cleaning & Preprocessing NLP Tokens...",
            "Extracting Skills, Experience & Education...",
            "Calculating Multi-Factor ATS Readiness Score..."
        ];
        let stepIdx = 0;
        const stepInterval = setInterval(() => {
            stepIdx = (stepIdx + 1) % steps.length;
            if (loadingStatusText) loadingStatusText.innerText = steps[stepIdx];
        }, 800);

        try {
            const formData = new FormData();
            if (hasFile) {
                formData.append('resume_file', fileInput.files[0]);
            } else {
                formData.append('resume_text', rawText);
            }
            if (jdText) {
                formData.append('jd_text', jdText);
            }

            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            clearInterval(stepInterval);
            loadingCard.style.display = 'none';

            if (result.status === 'success') {
                currentAnalysisData = result;
                renderDashboard(result);
                resultsDashboard.style.display = 'block';
                resultsDashboard.scrollIntoView({ behavior: 'smooth' });
            } else {
                inputCard.style.display = 'block';
                alert(result.message || 'Analysis failed. Please try again.');
            }

        } catch (err) {
            clearInterval(stepInterval);
            loadingCard.style.display = 'none';
            inputCard.style.display = 'block';
            alert('An error occurred during communication with ResumeIQ API.');
            console.error(err);
        }
    });

    // -------------------------------------------------------------
    // 8. DASHBOARD RENDERING
    // -------------------------------------------------------------
    function renderDashboard(data) {
        const ext = data.extracted_data;
        const score = data.score;
        const feedback = data.feedback;
        const wordFreq = data.word_frequencies;
        const jdMatch = data.jd_match;

        // Toolbar file name
        document.getElementById('resultFileTag').innerHTML = `<i class="fa-solid fa-file-lines"></i> ${data.filename}`;

        // 8.1 Score & Grade
        const total = score.total_score;
        document.getElementById('totalScoreNum').innerText = total;
        document.getElementById('gradeBadge').innerText = score.grade;
        document.getElementById('gradeLabel').innerText = score.grade_label;

        // Circle stroke dash animation
        const circleFill = document.getElementById('scoreCircleFill');
        if (circleFill) {
            circleFill.setAttribute('stroke-dasharray', `${total}, 100`);
            if (total >= 80) {
                circleFill.style.stroke = 'var(--accent-emerald)';
            } else if (total >= 60) {
                circleFill.style.stroke = 'var(--accent-amber)';
            } else {
                circleFill.style.stroke = 'var(--accent-rose)';
            }
        }

        // Subscores
        const bd = score.breakdown;
        setSubscore('subSkillsVal', 'barSkills', bd.skills_score, 25);
        setSubscore('subExpVal', 'barExp', bd.experience_score, 25);
        setSubscore('subEduVal', 'barEdu', bd.education_score, 15);
        setSubscore('subImpactVal', 'barImpact', bd.impact_score, 15);
        setSubscore('subContactVal', 'barContact', bd.contact_score, 10);
        setSubscore('subFormatVal', 'barFormat', bd.formatting_score, 10);

        // 8.2 Candidate Profile
        const contact = ext.contact;
        document.getElementById('candidateName').innerText = contact.name || 'Candidate';
        document.getElementById('candidateLocation').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${contact.location || 'Location Not Specified'}`;
        document.getElementById('candidateEmail').innerText = contact.email || 'Email Not Specified';
        document.getElementById('candidatePhone').innerText = contact.phone || 'Phone Not Specified';

        // Links
        const linksRow = document.getElementById('profileLinksRow');
        linksRow.innerHTML = '';
        if (contact.linkedin) {
            linksRow.innerHTML += `<a href="${contact.linkedin}" target="_blank" rel="noopener" class="link-btn"><i class="fa-brands fa-linkedin"></i> LinkedIn</a>`;
        }
        if (contact.github) {
            linksRow.innerHTML += `<a href="${contact.github}" target="_blank" rel="noopener" class="link-btn"><i class="fa-brands fa-github"></i> GitHub</a>`;
        }
        if (contact.portfolio) {
            linksRow.innerHTML += `<a href="${contact.portfolio}" target="_blank" rel="noopener" class="link-btn"><i class="fa-solid fa-globe"></i> Portfolio</a>`;
        }

        // Stats boxes
        document.getElementById('statSkillCount').innerText = ext.skills.total_count;
        document.getElementById('statExpYears').innerText = `${ext.experience.estimated_years} Yrs`;
        document.getElementById('statWordCount').innerText = ext.raw_word_count.toLocaleString();

        // Strengths
        const strengthsList = document.getElementById('strengthsList');
        strengthsList.innerHTML = '';
        (score.strengths || []).forEach(s => {
            const li = document.createElement('li');
            li.innerText = s;
            strengthsList.appendChild(li);
        });

        // 8.3 Categorized Skills Matrix
        renderSkills(ext.skills);

        // 8.4 Work Experience Timeline
        renderExperience(ext.experience.history);

        // 8.5 Extracted Projects
        renderProjects(ext.projects);

        // 8.6 Education & Certifications
        renderEducation(ext.education);
        renderCertifications(ext.certifications);

        // 8.7 Feedback & Power Verbs
        renderFeedback(feedback);

        // 8.8 Word Frequencies Cloud
        renderKeywords(wordFreq);

        // 8.9 Job Description Benchmark (if available)
        renderJdMatch(jdMatch);
    }

    function setSubscore(valId, barId, val, max) {
        const valElem = document.getElementById(valId);
        const barElem = document.getElementById(barId);
        if (valElem) valElem.innerText = `${val}/${max}`;
        if (barElem) {
            const pct = Math.min(100, Math.round((val / max) * 100));
            barElem.style.width = `${pct}%`;
        }
    }

    function renderSkills(skillsData) {
        const totalBadge = document.getElementById('skillsTotalCountBadge');
        if (totalBadge) totalBadge.innerText = skillsData.total_count;

        const filtersContainer = document.getElementById('categoryFilters');
        const categoriesContainer = document.getElementById('skillsCategoriesContainer');
        filtersContainer.innerHTML = '';
        categoriesContainer.innerHTML = '';

        const categories = skillsData.by_category;
        const categoryNames = Object.keys(categories);

        if (categoryNames.length === 0) {
            categoriesContainer.innerHTML = '<p class="text-secondary">No standardized technical skills detected.</p>';
            return;
        }

        // All filter button
        const allBtn = document.createElement('button');
        allBtn.className = 'filter-btn active';
        allBtn.innerText = `All (${skillsData.total_count})`;
        allBtn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            allBtn.classList.add('active');
            document.querySelectorAll('.category-block').forEach(b => b.style.display = 'block');
        });
        filtersContainer.appendChild(allBtn);

        categoryNames.forEach(cat => {
            const skillsInCat = categories[cat];
            
            // Filter button
            const catBtn = document.createElement('button');
            catBtn.className = 'filter-btn';
            catBtn.innerText = `${cat} (${skillsInCat.length})`;
            catBtn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                catBtn.classList.add('active');
                document.querySelectorAll('.category-block').forEach(b => {
                    b.style.display = (b.dataset.category === cat) ? 'block' : 'none';
                });
            });
            filtersContainer.appendChild(catBtn);

            // Block
            const block = document.createElement('div');
            block.className = 'category-block';
            block.dataset.category = cat;

            let pillsHtml = skillsInCat.map(s => `<span class="skill-tag">${s}</span>`).join('');
            block.innerHTML = `
                <div class="category-header">
                    <span class="category-name">${cat}</span>
                    <span class="category-count">${skillsInCat.length} skills</span>
                </div>
                <div class="skill-tags-group">${pillsHtml}</div>
            `;
            categoriesContainer.appendChild(block);
        });
    }

    function renderExperience(history) {
        const timeline = document.getElementById('experienceTimeline');
        timeline.innerHTML = '';

        if (!history || history.length === 0) {
            timeline.innerHTML = '<p class="text-secondary">No structured work experience blocks detected.</p>';
            return;
        }

        history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'timeline-item';

            let bulletsHtml = (item.highlights || []).map(b => `<li>${b}</li>`).join('');
            div.innerHTML = `
                <div class="timeline-role">${item.title}</div>
                <div class="timeline-company">
                    <span>${item.company}</span>
                    <span class="timeline-date">${item.duration}</span>
                </div>
                ${bulletsHtml ? `<ul class="timeline-bullets">${bulletsHtml}</ul>` : ''}
            `;
            timeline.appendChild(div);
        });
    }

    function renderProjects(projects) {
        const list = document.getElementById('projectsList');
        list.innerHTML = '';

        if (!projects || projects.length === 0) {
            list.innerHTML = '<p class="text-secondary">No separate projects section identified.</p>';
            return;
        }

        projects.forEach(p => {
            const item = document.createElement('div');
            item.className = 'project-item';

            let bullets = (p.details || []).map(d => `<li>${d}</li>`).join('');
            item.innerHTML = `
                <div class="project-title">${p.name}</div>
                ${p.tech_stack ? `<div class="project-stack">${p.tech_stack}</div>` : ''}
                ${bullets ? `<ul class="project-bullets">${bullets}</ul>` : ''}
            `;
            list.appendChild(item);
        });
    }

    function renderEducation(eduList) {
        const list = document.getElementById('educationList');
        list.innerHTML = '';

        if (!eduList || eduList.length === 0) {
            list.innerHTML = '<p class="text-secondary">No explicit education records detected.</p>';
            return;
        }

        eduList.forEach(e => {
            const div = document.createElement('div');
            div.className = 'edu-item';
            div.innerHTML = `
                <div class="edu-degree">${e.degree} - ${e.major}</div>
                <div class="edu-institution">${e.institution}</div>
                <div class="edu-meta">
                    ${e.year ? `<span>Graduation: ${e.year}</span>` : ''}
                    ${e.gpa ? ` • <span>GPA/Score: ${e.gpa}</span>` : ''}
                </div>
            `;
            list.appendChild(div);
        });
    }

    function renderCertifications(certs) {
        const list = document.getElementById('certificationsList');
        list.innerHTML = '';

        if (!certs || certs.length === 0) {
            list.innerHTML = '<p class="text-secondary">No industry certifications detected.</p>';
            return;
        }

        certs.forEach(c => {
            const div = document.createElement('div');
            div.className = 'cert-item';
            div.innerHTML = `<i class="fa-solid fa-award"></i> <span>${c}</span>`;
            list.appendChild(div);
        });
    }

    function renderFeedback(feedback) {
        const list = document.getElementById('feedbackList');
        list.innerHTML = '';

        const items = feedback.items || [];
        if (items.length === 0) {
            list.innerHTML = '<p class="text-success"><i class="fa-solid fa-circle-check"></i> Great job! No critical issues or weak language detected.</p>';
            return;
        }

        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'feedback-card-item';

            const pClass = item.priority === 'High' ? 'priority-high' : (item.priority === 'Medium' ? 'priority-medium' : 'priority-low');

            let examplesHtml = '';
            if (item.examples && item.examples.length > 0) {
                examplesHtml = '<div class="verb-examples"><strong>Suggested Replacements:</strong> ';
                examplesHtml += item.examples.map(ex => `<code>${ex.phrase}</code> &rarr; <em>${ex.alternatives.slice(0, 3).join(', ')}</em>`).join('<br>');
                examplesHtml += '</div>';
            }

            card.innerHTML = `
                <div class="feedback-header">
                    <span class="category-name text-primary">${item.category}</span>
                    <span class="priority-badge ${pClass}">${item.priority} Priority</span>
                </div>
                <h4 class="feedback-title">${item.title}</h4>
                <p class="feedback-desc">${item.description}</p>
                ${examplesHtml}
            `;
            list.appendChild(card);
        });
    }

    function renderKeywords(wordFreq) {
        const cloud = document.getElementById('keywordsCloud');
        cloud.innerHTML = '';

        if (!wordFreq || wordFreq.length === 0) {
            cloud.innerHTML = '<p class="text-secondary">No frequent keywords calculated.</p>';
            return;
        }

        wordFreq.forEach(([word, count]) => {
            const badge = document.createElement('div');
            badge.className = 'keyword-badge';
            badge.innerHTML = `${word} <span>×${count}</span>`;
            cloud.appendChild(badge);
        });
    }

    function renderJdMatch(jdMatch) {
        const jdCard = document.getElementById('jdMatchCard');
        if (!jdMatch) {
            jdCard.style.display = 'none';
            return;
        }

        jdCard.style.display = 'block';
        document.getElementById('jdMatchScore').innerText = `${jdMatch.match_score}%`;
        document.getElementById('jdMatchVerdict').innerText = jdMatch.verdict;

        // Matching skills
        const matchingContainer = document.getElementById('matchingSkillsPills');
        matchingContainer.innerHTML = '';
        document.getElementById('matchingSkillsCount').innerText = jdMatch.matching_skills.length;
        if (jdMatch.matching_skills.length > 0) {
            jdMatch.matching_skills.forEach(s => {
                const pill = document.createElement('span');
                pill.className = 'pill-match success';
                pill.innerHTML = `<i class="fa-solid fa-check"></i> ${s}`;
                matchingContainer.appendChild(pill);
            });
        } else {
            matchingContainer.innerHTML = '<span class="text-muted">None detected.</span>';
        }

        // Missing skills
        const missingContainer = document.getElementById('missingSkillsPills');
        missingContainer.innerHTML = '';
        document.getElementById('missingSkillsCount').innerText = jdMatch.missing_skills.length;
        if (jdMatch.missing_skills.length > 0) {
            jdMatch.missing_skills.forEach(s => {
                const pill = document.createElement('span');
                pill.className = 'pill-match danger';
                pill.innerHTML = `<i class="fa-solid fa-plus"></i> ${s}`;
                missingContainer.appendChild(pill);
            });
        } else {
            missingContainer.innerHTML = '<span class="text-success">Zero missing skills! Perfect match.</span>';
        }

        // Tips
        const tipsList = document.getElementById('tailoringTipsList');
        tipsList.innerHTML = '';
        (jdMatch.tailoring_tips || []).forEach(t => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fa-solid fa-circle-arrow-right"></i> ${t}`;
            tipsList.appendChild(li);
        });
    }

    // -------------------------------------------------------------
    // 9. TOOLBAR ACTIONS (Print, Export JSON, Reset)
    // -------------------------------------------------------------
    document.getElementById('printReportBtn')?.addEventListener('click', () => {
        window.print();
    });

    document.getElementById('downloadJsonBtn')?.addEventListener('click', () => {
        if (!currentAnalysisData) return;
        const blob = new Blob([JSON.stringify(currentAnalysisData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resumeiq_analysis_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    document.getElementById('resetBtn')?.addEventListener('click', () => {
        resultsDashboard.style.display = 'none';
        inputCard.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
