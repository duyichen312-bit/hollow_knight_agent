import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import cv2
from core.brain.vlm_planner import VLMPlanner, extract_json_from_text
from PIL import Image
from google.genai import types

vlm = VLMPlanner()
frame = cv2.imread("D:\\antigravity\\hollow_knight_agent\\assets\\live_hud.jpg")
small_frame = cv2.resize(frame, (640, 360))
rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
pil_img = Image.fromarray(rgb_frame)

print("Sending prompt to Gemini...")
response = vlm.gemini_client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[pil_img, "Return pure JSON object with key 'test': 'value'."],
    config=types.GenerateContentConfig(response_mime_type="application/json")
)
print("response.text:", repr(response.text))
data = extract_json_from_text(response.text)
print("parsed data:", data)
