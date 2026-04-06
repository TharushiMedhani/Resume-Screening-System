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
    filename: str = ""

class MultiAnalysisResponse(BaseModel):
    results: list[AnalysisResponse]