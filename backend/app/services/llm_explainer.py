import os
import re
from dotenv import load_dotenv, find_dotenv
from google import genai

load_dotenv(find_dotenv())
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    # Fallback to backend/.env if find_dotenv fails weirdly in some environments
    load_dotenv("backend/.env")
    API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in environment!")

client = genai.Client(api_key=API_KEY)


def generate_full_ai_analysis(job_description, resume_skills, matched_skills, missing_skills, match_score, recommendation):
    """
    Unified function to generate both AI explanation and interview questions in one API call.
    Handles quota errors gracefully and ensures non-empty strings are returned.
    """
    try:
        # Construct a single, focused prompt for 3-4 sentences of explanation and 6 questions
        prompt = f"""
        You are an experienced technical recruiter and interviewer.

        Analyze the candidate-job fit using only the information provided below.

        Job Description:
        {job_description}

        Resume Skills:
        {', '.join(resume_skills)}

        Matched Skills:
        {', '.join(matched_skills)}

        Missing Skills:
        {', '.join(missing_skills)}

        Match Score:
        {match_score}%

        Recommendation:
        {recommendation}

        Your tasks:
        1. Write a short professional explanation of the candidate’s suitability for the role in 3 to 4 sentences.
        2. Generate 6 interview questions:
           - 3 technical questions based on matched skills
           - 2 questions to assess missing skills or learning ability
           - 1 behavioral question

        Strict rules:
        - Do not invent skills, experience, or qualifications
        - Use only the given information
        - Keep the explanation clear, professional, and concise
        - Keep interview questions relevant to the role
        - Do not include headings like [SECTION]
        - Return the output in this exact format:

        Explanation:
        <write the explanation here>

        Interview Questions:
        - Question 1
        - Question 2
        - Question 3
        - Question 4
        - Question 5
        - Question 6
        """

        import time
        max_retries = 2
        retry_delay = 5
        
        full_text = ""
        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={
                        'max_output_tokens': 2048,
                        'temperature': 0.1,
                    }
                )
                
                if response and getattr(response, 'text', None):
                    full_text = response.text
                    break 
                
            except Exception as e:
                err_msg = str(e)
                # Check for rate limit / quota errors
                if any(x in err_msg.lower() for x in ["429", "limit", "quota", "exhausted"]) and attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                else:
                    # Log internally if needed, but return user-friendly message
                    print(f"LLM Error on attempt {attempt}: {err_msg}")
                    break
        
        # If we failed to get text after retries or non-quota error
        if not full_text:
             return (
                 "AI analysis is temporarily unavailable. Please try again shortly.",
                 "Interview questions are currently unavailable. Please try again shortly."
             )

        # Parsing logic to split Explanation and Interview Questions
        ai_explanation = ""
        interview_questions = ""

        if "Explanation:" in full_text and "Interview Questions:" in full_text:
            parts = full_text.split("Interview Questions:")
            ai_explanation = parts[0].replace("Explanation:", "").strip()
            interview_questions = parts[1].strip()
        else:
            # Fallback if AI deviated from format
            ai_explanation = full_text.split("\n\n")[0] # Take first paragraph as explanation
            interview_questions = "No formulated questions available. Check detailed analysis."

        # Ensure we never return an empty string
        ai_explanation = ai_explanation if ai_explanation else "Analysis summary could not be extracted correctly."
        interview_questions = interview_questions if interview_questions else "Questions could not be extracted correctly."

        return ai_explanation, interview_questions

    except Exception as e:
        print(f"Fatal Service Error: {str(e)}")
        return (
            "AI analysis is temporarily unavailable. Please try again shortly.",
            "Interview questions are currently unavailable. Please try again shortly."
        )
