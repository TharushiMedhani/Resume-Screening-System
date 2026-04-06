import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    response = client.models.generate_content(
        model="gemini-3-flash",
        contents="Say Hello"
    )
    print("Response text:", response.text)
except Exception as e:
    print("Error during Gemini API call:", str(e))
