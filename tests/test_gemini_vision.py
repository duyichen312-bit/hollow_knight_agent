import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv("C:\\Users\\ShenCongwen\\.gemini\\antigravity\\scratch\\hollow_knight_agent\\.env")
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

img_path = "C:\\Users\\ShenCongwen\\.gemini\\antigravity\\brain\\c806d348-fe9c-4be8-932f-3decf61eaa82\\.user_uploaded\\media_1787504190811.png"
pil_img = Image.open(img_path)

prompt = """
You are the AI Grandmaster playing Hollow Knight (空洞骑士).
Analyze this exact game frame.

Context Knowledge:
- Stage: King's Pass (国王山道), the tutorial area of Hallownest.
- Player: The Knight (white horned mask, gray cloak)
- Controls:
  - Jump: Hold Jump (Z/Space)
  - Attack / Break Barrier: Slash Nail (X/J)
  - Downward Pogo Slash: Down + Attack (Down+X)
  - Move Left/Right: Arrow Keys / A/D

Analyze what is on screen:
1. Identify the Knight's position and status.
2. Identify immediate obstacles or objects (e.g., breakable wooden doors, crawling bugs, geo clusters, spikes, ledges).
3. Prescribe the next sequence of game inputs to make progress in the walkthrough.

Output a valid JSON object ONLY:
{
  "room_name": "King's Pass",
  "scene_description": "<description>",
  "immediate_hazard_or_target": "<target>",
  "primary_action": "ATTACK_BARRIER" | "EXPLORE_RIGHT" | "JUMP_LEDGE" | "KILL_ENEMY" | "POGO_HAZARD",
  "sub_actions": ["MOVE_RIGHT", "ATTACK", "ATTACK", "JUMP"],
  "tactical_guidance": "<walkthrough advice>"
}
"""

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[pil_img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    print("Gemini 3.6 Flash Response:\n", response.text)
except Exception as e:
    print("Gemini call error:", e)
