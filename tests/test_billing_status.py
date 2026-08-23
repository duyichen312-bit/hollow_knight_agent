import os
from dotenv import load_dotenv
from google import genai

load_dotenv("C:\\Users\\ShenCongwen\\.gemini\\antigravity\\scratch\\hollow_knight_agent\\.env")
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("Testing Gemini 3.6 Flash API status...")
try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Hello Gemini! Are you ready for Hollow Knight gaming?"
    )
    print("\n[SUCCESS] API Response received:\n", response.text)
    print("\n>>> Your Gemini 3.6 Flash connection is active and healthy! <<<")
except Exception as e:
    print("\n[INFO] Gemini returned:", e)
