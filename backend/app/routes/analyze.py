import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.extractor import extract_text
from app.services.preprocess import clean_text
from app.services.skill_matcher import compare_skills
from app.services.similarity import calculate_similarity, get_recommendation, generate_analysis
from app.models.schemas import AnalysisResponse, MultiAnalysisResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_resume(resume: UploadFile, job_description: str) -> AnalysisResponse:
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    
    try:
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
    explanation, insights = generate_analysis(
        match_score, 
        skill_result["matched_skills"], 
        skill_result["job_skills"], 
        skill_result["missing_skills"]
    )

    return AnalysisResponse(
        match_score=match_score,
        recommendation=recommendation,
        resume_skills=skill_result["resume_skills"],
        job_skills=skill_result["job_skills"],
        matched_skills=skill_result["matched_skills"],
        missing_skills=skill_result["missing_skills"],
        explanation=explanation,
        insights=insights,
        filename=resume.filename
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    if not resume.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    try:
        return await process_resume(resume, job_description)
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR IN /analyze:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analyze-multiple", response_model=MultiAnalysisResponse)
async def analyze_multiple_resumes(
    resumes: list[UploadFile] = File(...),
    job_description: str = Form(...)
):
    if not resumes:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    results = []
    for resume in resumes:
        if not resume.filename.lower().endswith((".pdf", ".docx")):
            continue # Skip invalid files

        try:
            result = await process_resume(resume, job_description)
            results.append(result)
        except Exception as e:
            print(f"ERROR processing {resume.filename}: {str(e)}")
            # For multiple resumes, we might want to continue rather than fail all
            continue

    # Sort results by match_score descending
    results.sort(key=lambda x: x.match_score, reverse=True)

    return MultiAnalysisResponse(results=results)