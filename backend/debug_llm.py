import os
import re
from dotenv import load_dotenv, find_dotenv
from google import genai

load_dotenv(find_dotenv('backend/.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

print(f"DEBUG: API Key present: {bool(API_KEY)}")
if API_KEY:
    print(f"DEBUG: First few chars: {API_KEY[:5]}")

client = genai.Client(api_key=API_KEY)

def test_single():
    try:
        prompt = "Say hello and then [SEP] say world"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        print(f"DEBUG: LLM Text: {response.text}")
        if "[SEP]" in response.text:
            parts = response.text.split("[SEP]")
            print(f"DEBUG: Split Works! {parts}")
        else:
            print("DEBUG: [SEP] marker was missed by model")
    except Exception as e:
        print(f"DEBUG: Error caught: {str(e)}")

if __name__ == "__main__":
    test_single()
