import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from google import genai

api_key = os.getenv("GEMINI_API_KEY")
print(f"[Test] Using API Key: {api_key[:8]}...{api_key[-4:]}")

client = genai.Client(api_key=api_key)

print("[Test] Sending ping test to Gemini...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello! Confirm connection for Hollow Knight AI Agent in 1 short sentence."
    )
    print(f"[Test] Success! Response: {response.text.strip()}")
except Exception as e:
    print(f"[Test] Gemini 2.5 Flash error: {e}, trying fallback...")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello! Confirm connection for Hollow Knight AI Agent."
        )
        print(f"[Test] Fallback Success! Response: {response.text.strip()}")
    except Exception as e2:
        print(f"[Test] Fallback error: {e2}")
