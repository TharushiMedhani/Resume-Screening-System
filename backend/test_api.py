import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
print(f"API Key exists: {'Yes' if key else 'No'}")

try:
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say Hello"
    )
    print("Response text:", response.text)
except Exception as e:
    print("Error during Gemini API call:", str(e))
