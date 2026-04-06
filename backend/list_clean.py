import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    models = list(client.models.list())
    for model in models:
        # Just print the short ID part
        short_id = model.name.split('/')[-1]
        print(f"{short_id}")
except Exception as e:
    print("Error:", str(e))
