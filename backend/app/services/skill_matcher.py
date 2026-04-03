import re
from app.utils.skills import SKILLS

# Predefined aliases to improve detection accuracy
ALIASES = {
    "react": ["reactjs", "react.js", "react js"],
    "node.js": ["nodejs", "node js", "node.js"],
    "javascript": ["js", "javascript", "ecmascript"],
    "typescript": ["ts", "typescript"],
    "aws": ["amazon web services", "aws"],
    "google cloud": ["gcp", "google cloud platform"],
    "c#": ["csharp", "c#"],
    "c++": ["cpp", "c++"],
    "postgresql": ["postgres", "postgresql", "postgre"],
    "mysql": ["my sql", "mysql"],
    "redux": ["redux", "redux toolkit"],
    "project management": ["project management", "pm", "project manager", "pmp"],
}

# Skill Families (General requirements -> Specific cv skills)
FAMILIES = {
    "sql": ["mysql", "postgresql", "sql server", "sqlite", "oracle", "mariadb"],
    "databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "nosql", "dynamodb"],
    "cloud": ["aws", "azure", "google cloud", "gcp", "heroku", "digitalocean"],
    "frontend": ["html", "css", "javascript", "react", "vue", "angular", "next.js"],
    "docker": ["kubernetes", "containers", "docker-compose"],
    "ml": ["machine learning", "tensorflow", "pytorch", "deep learning", "nlp"],
}

def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found_skills = set()

    for skill in SKILLS:
        skill_lower = skill.lower()
        
        synonyms = [skill_lower]
        if skill_lower in ALIASES:
            synonyms.extend(ALIASES[skill_lower])
            
        for syn in set(synonyms):
            pattern = rf"(?<![a-zA-Z0-9]){re.escape(syn)}(?![a-zA-Z0-9])"
            if re.search(pattern, text_lower):
                found_skills.add(skill)
                break
                
    return sorted(list(found_skills))

def compare_skills(resume_text: str, job_text: str) -> dict:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    # Convert to set for matching
    matched_skills = set(resume_skills) & set(job_skills)
    
    # Hierarchical matching
    # If Job has "sql" but resume missed it, check if resume has "mysql"
    pending_job_skills = set(job_skills) - matched_skills
    additional_matched = set()

    resume_skills_lower = [s.lower() for s in resume_skills]

    for j_skill in pending_job_skills:
        j_lower = j_skill.lower()
        if j_lower in FAMILIES:
            # If any skill in the family is in the resume
            family_members = FAMILIES[j_lower]
            if any(member in resume_skills_lower for member in family_members):
                additional_matched.add(j_skill)
    
    final_matched = sorted(list(matched_skills | additional_matched))
    final_missing = sorted(list(set(job_skills) - set(final_matched)))

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": final_matched,
        "missing_skills": final_missing
    }
