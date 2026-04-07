import os
from dotenv import load_dotenv, find_dotenv
from google import genai

load_dotenv(find_dotenv())

api_key = os.getenv("GOOGLE_API_KEY")
print("INTERVIEW_GENERATOR - GOOGLE_API_KEY loaded:", bool(api_key))

client = genai.Client(api_key=api_key)

def generate_interview_questions(job_description, resume_skills, matched_skills, missing_skills):
    resume_skills = resume_skills or []
    matched_skills = matched_skills or []
    missing_skills = missing_skills or []
    job_description = job_description or ""

    print("Generating interview questions...")
    print("Job Description:", job_description[:200])
    print("Resume Skills:", resume_skills)
    print("Matched Skills:", matched_skills)
    print("Missing Skills:", missing_skills)

    prompt = f"""
You are an experienced technical interviewer.

STRICT RULES:
- Do NOT invent skills not listed
- Questions must be relevant to the job role
- Mix difficulty levels

INPUT:

Job Description:
{job_description}

Candidate Skills:
{', '.join(resume_skills)}

Matched Skills:
{', '.join(matched_skills)}

Missing Skills:
{', '.join(missing_skills)}

TASK:
Generate:
- 3 technical questions
- 2 skill gap questions
- 1 behavioral question

FORMAT:
Use bullet points.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print("Interview LLM raw response:", response)
        print("Interview LLM text:", getattr(response, "text", None))
        return getattr(response, "text", "No questions generated")

    except Exception as e:
        print("Interview LLM ERROR:", str(e))
        return "Interview questions unavailable"