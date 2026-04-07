import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.extractor import extract_text
from app.services.preprocess import clean_text
from app.services.skill_matcher import compare_skills
from app.services.similarity import calculate_similarity, get_recommendation, generate_analysis
from app.models.schemas import AnalysisResponse, MultiAnalysisResponse
from app.services.llm_explainer import generate_full_ai_analysis

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_resume(resume: UploadFile, job_description: str, skip_llm: bool = False) -> AnalysisResponse:
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    
    try:
        # Check if it's already a file (spooled)
        if hasattr(resume.file, 'read'):
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)
        
        resume_text = extract_text(file_path)
    finally:
        # Delete file after text extraction
        if os.path.exists(file_path):
            os.remove(file_path)

    if not resume_text or not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract text from {resume.filename}."
        )

    cleaned_resume = clean_text(resume_text)
    cleaned_job = clean_text(job_description)

    skill_result = compare_skills(cleaned_resume, cleaned_job)
    
    match_score = calculate_similarity(
        cleaned_resume, 
        cleaned_job, 
        skill_result["matched_skills"], 
        skill_result["job_skills"]
    )
    
    recommendation = get_recommendation(match_score)
    
    # Use rule-based (TF-IDF/Skill Match) analysis as a reliable baseline
    explanation, insights = generate_analysis(
        match_score, 
        skill_result["matched_skills"], 
        skill_result["job_skills"], 
        skill_result["missing_skills"]
    )

    ai_explanation, interview_questions = "", ""
    if not skip_llm:
        # Unified call for ONLY the detailed AI content
        # Still keeps one combined call internally for efficiency
        ai_explanation, interview_questions = generate_full_ai_analysis(
            job_description=job_description,
            resume_skills=skill_result["resume_skills"],
            matched_skills=skill_result["matched_skills"],
            missing_skills=skill_result["missing_skills"],
            match_score=match_score,
            recommendation=recommendation
        )
    else:
        ai_explanation = "Select this resume to view detailed AI analysis."
        interview_questions = ""

    return AnalysisResponse(
        match_score=match_score,
        recommendation=recommendation,
        resume_skills=skill_result["resume_skills"],
        job_skills=skill_result["job_skills"],
        matched_skills=skill_result["matched_skills"],
        missing_skills=skill_result["missing_skills"],
        explanation=explanation,
        insights=insights,
        ai_explanation=ai_explanation,
        interview_questions=interview_questions,
        filename=resume.filename
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    return await process_resume(resume, job_description)


@router.post("/analyze-multiple", response_model=MultiAnalysisResponse)
async def analyze_multiple_resumes(
    resumes: list[UploadFile] = File(...),
    job_description: str = Form(...)
):
    if not resumes:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    # 1. Process all resumes for scoring ONLY (skip LLM)
    results = []
    for resume in resumes:
        if not resume.filename.lower().endswith((".pdf", ".docx")):
            continue
        try:
            res_obj = await process_resume(resume, job_description, skip_llm=True)
            results.append(res_obj)
        except Exception as e:
            print(f"ERROR scoring {resume.filename}: {str(e)}")
            continue

    if not results:
        return MultiAnalysisResponse(results=[])

    # 2. Sort by match_score
    results.sort(key=lambda x: x.match_score, reverse=True)

    # 3. Trigger LLM for ONLY the top candidate
    top = results[0]
    try:
        # Generate the full analysis in one go
        ai_exp, int_q = generate_full_ai_analysis(
            job_description=job_description,
            resume_skills=top.resume_skills,
            matched_skills=top.matched_skills,
            missing_skills=top.missing_skills,
            match_score=top.match_score,
            recommendation=top.recommendation
        )
        top.ai_explanation = ai_exp
        top.interview_questions = int_q
    except Exception as e:
        print(f"TOP CANDIDATE LLM ERROR: {str(e)}")
        top.ai_explanation = "AI analysis is temporarily unavailable. Please try again shortly."
        top.interview_questions = "Questions unavailable."

    return MultiAnalysisResponse(results=results)