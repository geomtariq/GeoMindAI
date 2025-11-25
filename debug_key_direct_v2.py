import os
from google import genai
from dotenv import load_dotenv

# Force load from .env, overriding existing env vars
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found in .env")
    exit(1)

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, are you working?"
    )
    print(f"✅ API Key is VALID. Response: {response.text}")
except Exception as e:
    print(f"❌ API Key is INVALID or EXPIRED. Error: {e}")
