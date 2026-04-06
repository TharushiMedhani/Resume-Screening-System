import os
from dotenv import load_dotenv, find_dotenv
from google import genai

load_dotenv(find_dotenv())

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_ai_explanation(job_description, resume_skills, matched_skills, missing_skills, match_score, recommendation):


    prompt = f"""
You are helping recruiters evaluate candidate-job fit.

Job Description:
{job_description}

Resume Skills:
{', '.join(resume_skills)}

Matched Skills:
{', '.join(matched_skills)}

Missing Skills:
{', '.join(missing_skills)}

Match Score:
{match_score}

Recommendation:
{recommendation}

Write a short professional explanation (3-4 sentences).
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text