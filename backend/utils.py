"""
Advanced Utility functions for resume parsing and ATS scoring.
"""
import re
from io import BytesIO
from collections import Counter
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document


# ===== Common skill categories =====
TECHNICAL_SKILLS = {
    'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'nodejs',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes', 'aws',
    'azure', 'gcp', 'linux', 'git', 'jenkins', 'terraform', 'ansible', 'html', 'css',
    'api', 'rest', 'graphql', 'microservices', 'machine learning', 'ai', 'tensorflow',
    'pytorch', 'pandas', 'numpy', 'scikit', 'spark', 'hadoop', 'kafka', 'elasticsearch',
    'c++', 'golang', 'rust', 'swift', 'kotlin', 'flutter', 'react native', 'django',
    'flask', 'spring', 'nodejs', 'express', 'fastapi', 'devops', 'cicd', 'agile', 'scrum'
}

SOFT_SKILLS = {
    'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
    'critical thinking', 'creativity', 'adaptability', 'collaboration', 'management',
    'mentoring', 'presentation', 'negotiation', 'decision making', 'time management',
    'organization', 'attention to detail', 'multitasking', 'interpersonal', 'strategic'
}

TOOLS_PLATFORMS = {
    'jira', 'confluence', 'slack', 'trello', 'asana', 'github', 'gitlab', 'bitbucket',
    'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'excel', 'powerpoint',
    'tableau', 'power bi', 'salesforce', 'hubspot', 'zendesk', 'notion', 'monday',
    'postman', 'swagger', 'vs code', 'intellij', 'pycharm', 'android studio', 'xcode'
}

CERTIFICATIONS_KEYWORDS = {
    'certified', 'certification', 'certificate', 'aws certified', 'azure certified',
    'pmp', 'scrum master', 'csm', 'cka', 'ckad', 'comptia', 'cisco', 'ccna', 'ccnp',
    'google certified', 'meta certified', 'six sigma', 'itil', 'prince2'
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text content from a PDF file."""
    return extract_pdf_text(BytesIO(file_bytes))


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text content from a DOCX file."""
    doc = Document(BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


def clean_text(text: str) -> str:
    """Cleans and normalizes text for processing."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_keywords(text: str, min_length: int = 2) -> set:
    """Extracts unique keywords from text."""
    words = clean_text(text).split()
    return {word for word in words if len(word) >= min_length}


def extract_phrases(text: str) -> set:
    """Extracts two-word phrases for better matching."""
    words = clean_text(text).split()
    phrases = set()
    for i in range(len(words) - 1):
        phrases.add(f"{words[i]} {words[i+1]}")
    return phrases


def categorize_skills(keywords: set) -> dict:
    """Categorizes matched keywords into skill types."""
    categories = {
        'technical': [],
        'soft_skills': [],
        'tools': [],
        'certifications': [],
        'other': []
    }
    
    for keyword in keywords:
        kw_lower = keyword.lower()
        if kw_lower in TECHNICAL_SKILLS:
            categories['technical'].append(keyword)
        elif kw_lower in SOFT_SKILLS:
            categories['soft_skills'].append(keyword)
        elif kw_lower in TOOLS_PLATFORMS:
            categories['tools'].append(keyword)
        elif any(cert in kw_lower for cert in CERTIFICATIONS_KEYWORDS):
            categories['certifications'].append(keyword)
        else:
            categories['other'].append(keyword)
    
    return categories


def detect_resume_sections(resume_text: str) -> dict:
    """Detects and scores the presence of standard resume sections."""
    resume_lower = resume_text.lower()
    
    sections = {
        'contact_info': {
            'present': False,
            'keywords': ['email', 'phone', 'linkedin', 'github', 'address', '@'],
            'importance': 'critical'
        },
        'summary': {
            'present': False,
            'keywords': ['summary', 'objective', 'profile', 'about me'],
            'importance': 'recommended'
        },
        'experience': {
            'present': False,
            'keywords': ['experience', 'work history', 'employment', 'professional experience'],
            'importance': 'critical'
        },
        'education': {
            'present': False,
            'keywords': ['education', 'academic', 'degree', 'university', 'college', 'bachelor', 'master', 'phd'],
            'importance': 'critical'
        },
        'skills': {
            'present': False,
            'keywords': ['skills', 'technical skills', 'competencies', 'technologies'],
            'importance': 'critical'
        },
        'projects': {
            'present': False,
            'keywords': ['project', 'portfolio', 'personal project', 'team project'],
            'importance': 'recommended'
        },
        'certifications': {
            'present': False,
            'keywords': ['certification', 'certificate', 'licensed', 'accredited'],
            'importance': 'optional'
        },
        'achievements': {
            'present': False,
            'keywords': ['achievement', 'award', 'honor', 'recognition', 'accomplishment'],
            'importance': 'optional'
        }
    }
    
    for section_name, section_data in sections.items():
        for keyword in section_data['keywords']:
            if keyword in resume_lower:
                section_data['present'] = True
                break
    
    # Calculate section score
    critical_present = sum(1 for s in sections.values() if s['present'] and s['importance'] == 'critical')
    critical_total = sum(1 for s in sections.values() if s['importance'] == 'critical')
    
    section_score = round((critical_present / critical_total) * 100) if critical_total > 0 else 0
    
    return {
        'sections': {k: {'present': v['present'], 'importance': v['importance']} for k, v in sections.items()},
        'section_score': section_score
    }


def analyze_formatting(resume_text: str) -> dict:
    """Analyzes resume formatting and structure quality."""
    issues = []
    score = 100
    
    # Check length
    word_count = len(resume_text.split())
    if word_count < 150:
        issues.append({'type': 'warning', 'message': 'Resume is too short. Aim for 400-700 words.'})
        score -= 15
    elif word_count > 1200:
        issues.append({'type': 'warning', 'message': 'Resume is very long. Consider condensing to 1-2 pages.'})
        score -= 10
    
    # Check for action verbs
    action_verbs = ['achieved', 'improved', 'created', 'developed', 'led', 'managed', 
                    'increased', 'reduced', 'designed', 'implemented', 'launched', 
                    'built', 'optimized', 'streamlined', 'delivered', 'executed']
    resume_lower = resume_text.lower()
    verbs_found = sum(1 for verb in action_verbs if verb in resume_lower)
    
    if verbs_found < 3:
        issues.append({'type': 'warning', 'message': 'Use more action verbs to describe your achievements.'})
        score -= 10
    elif verbs_found >= 5:
        issues.append({'type': 'success', 'message': 'Good use of action verbs!'})
    
    # Check for metrics/numbers
    numbers = re.findall(r'\d+%?', resume_text)
    if len(numbers) < 3:
        issues.append({'type': 'warning', 'message': 'Add more quantifiable achievements with numbers.'})
        score -= 10
    elif len(numbers) >= 5:
        issues.append({'type': 'success', 'message': 'Good use of quantifiable metrics!'})
    
    # Check for common resume issues
    if 'references available' in resume_lower:
        issues.append({'type': 'error', 'message': 'Remove "References available upon request" - it\'s outdated.'})
        score -= 5
    
    if re.search(r'\b(i am|i have|i was)\b', resume_lower):
        issues.append({'type': 'warning', 'message': 'Avoid first-person pronouns. Use action verbs instead.'})
        score -= 5
    
    # Check for email
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        issues.append({'type': 'error', 'message': 'No email address detected. Ensure contact info is included.'})
        score -= 15
    else:
        issues.append({'type': 'success', 'message': 'Contact email detected.'})
    
    # Check for phone
    if not re.search(r'[\d\(\)\-\+\s]{10,}', resume_text):
        issues.append({'type': 'warning', 'message': 'Phone number may be missing or not detected.'})
        score -= 5
    
    return {
        'formatting_score': max(0, min(100, score)),
        'word_count': word_count,
        'issues': issues
    }


def calculate_keyword_density(resume_text: str, jd_text: str) -> dict:
    """Calculates keyword frequency and density analysis."""
    resume_words = clean_text(resume_text).split()
    jd_words = clean_text(jd_text).split()
    
    jd_word_freq = Counter(jd_words)
    resume_word_freq = Counter(resume_words)
    
    # Get top JD keywords (excluding common words)
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                   'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                   'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
                   'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from', 'as',
                   'this', 'that', 'these', 'those', 'it', 'its', 'they', 'their',
                   'we', 'our', 'you', 'your', 'he', 'she', 'him', 'her', 'his',
                   'who', 'what', 'when', 'where', 'why', 'how', 'which', 'all',
                   'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
                   'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                   'too', 'very', 'just', 'also', 'now', 'well', 'about', 'after',
                   'before', 'between', 'into', 'through', 'during', 'above', 'below'}
    
    important_jd_keywords = {word: count for word, count in jd_word_freq.items() 
                            if word not in common_words and len(word) > 2 and count > 1}
    
    top_keywords = sorted(important_jd_keywords.items(), key=lambda x: x[1], reverse=True)[:15]
    
    keyword_analysis = []
    for keyword, jd_count in top_keywords:
        resume_count = resume_word_freq.get(keyword, 0)
        keyword_analysis.append({
            'keyword': keyword,
            'jd_frequency': jd_count,
            'resume_frequency': resume_count,
            'present': resume_count > 0,
            'recommendation': 'add' if resume_count == 0 else ('increase' if resume_count < jd_count else 'good')
        })
    
    return {
        'keyword_density': keyword_analysis,
        'total_jd_words': len(jd_words),
        'total_resume_words': len(resume_words)
    }


def calculate_ats_score(resume_text: str, jd_text: str) -> dict:
    """
    Calculates a comprehensive ATS match score between a resume and job description.
    Uses keyword matching, phrase matching, and multiple analysis factors.
    """
    resume_keywords = get_keywords(resume_text)
    jd_keywords = get_keywords(jd_text)
    
    # Also check two-word phrases
    resume_phrases = extract_phrases(resume_text)
    jd_phrases = extract_phrases(jd_text)
    
    if not jd_keywords:
        return {"score": 0, "matched_keywords": [], "missing_keywords": [], 
                "keyword_score": 0, "similarity_score": 0, "phrase_score": 0}
    
    # Keyword matching
    matched_keywords = resume_keywords.intersection(jd_keywords)
    missing_keywords = jd_keywords.difference(resume_keywords)
    
    # Phrase matching
    matched_phrases = resume_phrases.intersection(jd_phrases)
    
    # Keyword match percentage
    keyword_score = (len(matched_keywords) / len(jd_keywords)) * 100 if jd_keywords else 0
    
    # Phrase match score (bonus)
    phrase_score = min(20, len(matched_phrases) * 2)  # Max 20 bonus points
    
    # Jaccard similarity
    union = resume_keywords.union(jd_keywords)
    jaccard_similarity = (len(matched_keywords) / len(union)) * 100 if union else 0
    
    # Combined score (weighted average with phrase bonus)
    base_score = (keyword_score * 0.6) + (jaccard_similarity * 0.3) + (phrase_score * 0.5)
    final_score = min(100, round(base_score, 1))
    
    # Categorize skills
    skill_categories = categorize_skills(matched_keywords)
    
    return {
        "score": final_score,
        "keyword_score": round(keyword_score, 1),
        "similarity_score": round(jaccard_similarity, 1),
        "phrase_score": round(phrase_score, 1),
        "matched_keywords": sorted(list(matched_keywords))[:50],
        "missing_keywords": sorted(list(missing_keywords))[:30],
        "matched_phrases": sorted(list(matched_phrases))[:20],
        "skill_categories": skill_categories
    }


def generate_suggestions(resume_text: str, jd_text: str, missing_keywords: list, 
                         formatting_analysis: dict, section_analysis: dict) -> list:
    """Generates comprehensive improvement suggestions based on all analyses."""
    suggestions = []
    
    resume_lower = resume_text.lower()
    
    # Priority 1: Critical missing sections
    for section_name, section_info in section_analysis['sections'].items():
        if not section_info['present'] and section_info['importance'] == 'critical':
            display_name = section_name.replace('_', ' ').title()
            suggestions.append({
                'priority': 'high',
                'category': 'structure',
                'title': f'Add {display_name} Section',
                'description': f'Your resume appears to be missing a {display_name} section. This is critical for ATS systems.'
            })
    
    # Priority 2: Important missing keywords
    jd_lower = jd_text.lower()
    keyword_freq = {kw: jd_lower.count(kw) for kw in missing_keywords}
    important_missing = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:8]
    
    if important_missing:
        kw_list = ", ".join([kw for kw, _ in important_missing[:5]])
        suggestions.append({
            'priority': 'high',
            'category': 'keywords',
            'title': 'Add Key Skills From Job Description',
            'description': f'Consider adding these important keywords: {kw_list}'
        })
    
    # Priority 3: Formatting issues
    for issue in formatting_analysis.get('issues', []):
        if issue['type'] == 'error':
            suggestions.append({
                'priority': 'high',
                'category': 'formatting',
                'title': 'Formatting Issue',
                'description': issue['message']
            })
        elif issue['type'] == 'warning':
            suggestions.append({
                'priority': 'medium',
                'category': 'formatting',
                'title': 'Improvement Suggestion',
                'description': issue['message']
            })
    
    # Priority 4: Content enhancements
    if not any(word in resume_lower for word in ['achieved', 'improved', 'increased', 'reduced', 'delivered']):
        suggestions.append({
            'priority': 'medium',
            'category': 'content',
            'title': 'Use Strong Action Verbs',
            'description': 'Start bullet points with action verbs like "Achieved", "Developed", "Led", "Improved", "Delivered".'
        })
    
    # Check for recommended sections
    for section_name, section_info in section_analysis['sections'].items():
        if not section_info['present'] and section_info['importance'] == 'recommended':
            display_name = section_name.replace('_', ' ').title()
            suggestions.append({
                'priority': 'low',
                'category': 'structure',
                'title': f'Consider Adding {display_name}',
                'description': f'A {display_name} section can strengthen your resume.'
            })
    
    # Positive feedback
    if not suggestions:
        suggestions.append({
            'priority': 'info',
            'category': 'general',
            'title': 'Great Job!',
            'description': 'Your resume covers all the basics. Focus on tailoring specific keywords to each job application.'
        })
    
    return suggestions


def generate_full_analysis(resume_text: str, jd_text: str) -> dict:
    """Generates a comprehensive resume analysis report."""
    
    # Calculate all scores
    ats_data = calculate_ats_score(resume_text, jd_text)
    section_analysis = detect_resume_sections(resume_text)
    formatting_analysis = analyze_formatting(resume_text)
    keyword_density = calculate_keyword_density(resume_text, jd_text)
    
    # Generate suggestions
    suggestions = generate_suggestions(
        resume_text, jd_text, 
        ats_data['missing_keywords'],
        formatting_analysis,
        section_analysis
    )
    
    # Calculate overall score (weighted)
    overall_score = round(
        (ats_data['score'] * 0.5) + 
        (section_analysis['section_score'] * 0.25) + 
        (formatting_analysis['formatting_score'] * 0.25)
    , 1)
    
    # Create resume text preview (first 500 chars, cleaned up)
    resume_preview = resume_text.strip()[:500]
    if len(resume_text.strip()) > 500:
        resume_preview += "..."
    
    # Generate top priority actions (top 3 actionable items)
    high_priority = [s for s in suggestions if s['priority'] == 'high'][:2]
    medium_priority = [s for s in suggestions if s['priority'] == 'medium'][:1]
    top_priority_actions = high_priority + medium_priority
    
    # Add keyword match counts for visualization
    keyword_match_stats = {
        'total_jd_keywords': len(get_keywords(jd_text)),
        'matched_count': len(ats_data['matched_keywords']),
        'missing_count': len(ats_data['missing_keywords']),
        'match_percentage': round(
            len(ats_data['matched_keywords']) / max(len(get_keywords(jd_text)), 1) * 100, 1
        )
    }
    
    return {
        'overall_score': overall_score,
        'ats_score': ats_data['score'],
        'keyword_match_score': ats_data['keyword_score'],
        'content_similarity_score': ats_data['similarity_score'],
        'section_score': section_analysis['section_score'],
        'formatting_score': formatting_analysis['formatting_score'],
        'matched_keywords': ats_data['matched_keywords'],
        'missing_keywords': ats_data['missing_keywords'],
        'matched_phrases': ats_data.get('matched_phrases', []),
        'skill_categories': ats_data['skill_categories'],
        'sections': section_analysis['sections'],
        'formatting_issues': formatting_analysis['issues'],
        'keyword_density': keyword_density['keyword_density'],
        'word_count': formatting_analysis['word_count'],
        'suggestions': suggestions,
        'resume_text_preview': resume_preview,
        'top_priority_actions': top_priority_actions,
        'keyword_match_stats': keyword_match_stats
    }

