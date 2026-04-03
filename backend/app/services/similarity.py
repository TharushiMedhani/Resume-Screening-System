from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(resume_text: str, job_text: str, matched_skills: list, job_skills: list) -> float:
    if not resume_text.strip() or not job_text.strip():
        return 0.0

    # 1. TF-IDF Text Similarity (40% weight)
    documents = [resume_text, job_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    text_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    text_score = text_sim * 100

    # 2. Skill Match Ratio (60% weight)
    if not job_skills:
        skill_score = text_score # Default to text score if no explicit skills found in JD
    else:
        # We give more weight to skills being present
        skill_score = (len(matched_skills) / len(job_skills)) * 100

    # Weighted Final Score
    final_score = (text_score * 0.4) + (skill_score * 0.6)
    
    return round(final_score, 2)

def generate_analysis(score: float, matched: list, job: list, missing: list) -> tuple[str, list[str]]:
    insights = []
    
    # Generate insights
    if len(job) > 0:
        match_rate = (len(matched) / len(job)) * 100
        insights.append(f"Skill Match Rate: {match_rate:.0f}% ({len(matched)} of {len(job)} core skills identified).")
    
    if len(matched) > 0:
        insights.append(f"Key strengths found: {', '.join(matched[:3])}{' and others' if len(matched) > 3 else ''}.")
    
    if len(missing) > 0:
        insights.append(f"Critical gaps: {', '.join(missing[:3])}.")
    else:
        insights.append("No critical skill gaps identified.")

    # Generate explanation
    if score >= 80:
        explanation = "Excellent match! The candidate's profile strongly aligns with the job requirements, showing both tool-set proficiency and semantic relevance."
    elif score >= 60:
        explanation = "Good match. The candidate has most of the required skills but may need minor upskilling in a few specific areas."
    elif score >= 40:
        explanation = "Moderate match. While the candidate has some relevant experience, there are significant gaps that should be addressed in an interview."
    else:
        explanation = "Weak match. The candidate's background does not align well with the primary requirements of this role."

    return explanation, insights

def get_recommendation(score: float) -> str:
    if score >= 85: return "Highly Recommended"
    if score >= 70: return "Strong Match"
    if score >= 50: return "Good Fit"
    if score >= 30: return "Potential Match"
    return "Not Recommended"
