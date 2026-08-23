import os
import sys
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv("D:\\antigravity\\hollow_knight_agent\\.env")
api_key = os.getenv("GEMINI_API_KEY")
print(f"Loaded GEMINI_API_KEY: {api_key[:10]}... (length {len(api_key) if api_key else 0})")

client = genai.Client(api_key=api_key)

img_path = "D:\\antigravity\\hollow_knight_agent\\assets\\live_hud.jpg"
if not os.path.exists(img_path):
    img_path = "C:\\Users\\ShenCongwen\\.gemini\\antigravity\\brain\\c806d348-fe9c-4be8-932f-3decf61eaa82\\.user_uploaded\\media_1787504190811.png"

pil_img = Image.open(img_path)
print(f"Loaded test image: {img_path} ({pil_img.size})")

prompt = """
You are the AI Gaming Grandmaster playing Hollow Knight (空洞骑士).
Analyze this exact gameplay screenshot.

Tell me:
1. What exact room/area is shown?
2. Where is the Knight standing and facing?
3. What is the immediate obstacle or objective?
4. What are the next 3 specific controller inputs needed?

Output pure JSON:
{
  "room": "Exact room name",
  "knight_status": "Knight position and situation",
  "immediate_target": "Wooden barrier / Crawlid / Spikes / Platform",
  "actions": ["JUMP_SLASH", "MOVE_RIGHT"],
  "tactical_guidance": "Detailed advice"
}
"""

print("\n--- Sending request to gemini-3.6-flash ---")
t0 = time.time()
try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[pil_img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    dt = time.time() - t0
    print(f"[SUCCESS] Got response in {dt:.2f}s:\n")
    print(response.text)
except Exception as e:
    dt = time.time() - t0
    print(f"[FAILED] Error after {dt:.2f}s:\n", repr(e))
