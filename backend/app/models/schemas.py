from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    match_score: float
    recommendation: str
    resume_skills: list[str]
    job_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
    insights: list[str]
    ai_explanation: str
    filename: str = ""
    interview_questions: str | None = None

class MultiAnalysisResponse(BaseModel):
    results: list[AnalysisResponse]
