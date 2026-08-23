import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv("D:\\antigravity\\hollow_knight_agent\\.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
img = Image.open("D:\\antigravity\\hollow_knight_agent\\assets\\live_hud.jpg")

res = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[img, """
你是《空洞骑士》AI。请输出严格 JSON：
{
  "current_location": "当前位置",
  "exploration_phase": "PHASE_1_BARRIER",
  "macro_goal": "宏观目标",
  "navigation_mode": "HORIZONTAL_EXPLORE",
  "direction": "RIGHT",
  "vertical_action": "NONE",
  "tactic": "战术"
}
"""]
)
print("--- RAW GEMINI RESPONSE TEXT ---")
print(res.text)
