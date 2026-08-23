import os
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv("D:\\antigravity\\hollow_knight_agent\\.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
img = Image.open("D:\\antigravity\\hollow_knight_agent\\assets\\live_hud.jpg")

print("Testing 3 consecutive high-speed multimodal requests...")
for i in range(3):
    t0 = time.time()
    res = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[img, f"Request #{i+1}: What is the immediate tactical directive? Output 1 sentence JSON."]
    )
    dt = time.time() - t0
    print(f"Request #{i+1} OK in {dt:.2f}s:\n{res.text.strip()}\n")
