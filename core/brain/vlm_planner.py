import os
import re
import time
import json
import base64
import cv2
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image
from dotenv import load_dotenv

from core.brain.profile_manager import ProfileManager

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def extract_json_from_text(text: str) -> Optional[dict]:
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"(\{[\s\S]*\})", cleaned)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None

class VLMPlanner:
    """
    Universal Multimodal Game Walkthrough Brain linked with ProfileManager.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Initialize Profile Manager
        self.pm = ProfileManager(self.base_dir)
        active_prof = self.pm.get_active_profile()

        self.provider = self.config.get("provider", active_prof.get("provider", "gemini")).lower()
        self.model_name = self.config.get("model", active_prof.get("model", "gemini-3.6-flash"))
        self.base_url = self.config.get("base_url", active_prof.get("base_url", ""))
        self.api_key_env = active_prof.get("api_key_env", "GEMINI_API_KEY")
        self.api_key = self.pm.get_api_key_for_env(self.api_key_env)
        
        self.gemini_client = None
        self.openai_client = None
        
        self.last_query_time = 0.0
        self.query_interval = float(self.config.get("decision_interval_sec", active_prof.get("decision_interval_sec", 2.0)))
        self.backoff_until = 0.0
        self.last_known_health = 5

        # Initialize Logs Directory
        self.logs_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.jsonl_log_path = os.path.join(self.logs_dir, "vlm_decisions.jsonl")
        self.text_log_path = os.path.join(self.logs_dir, "vlm_journal.log")

        self.current_strategy: Dict[str, Any] = {
            "current_location": "King's Pass (国王山道起始区)",
            "exploration_phase": "PHASE_1_BARRIER",
            "macro_goal": "向前探索并斩碎木门，跃下深坑进入下层",
            "navigation_mode": "HORIZONTAL_AND_UPWARD_CLIMB",
            "direction": "RIGHT",
            "vertical_action": "JUMP_CLIMB_UP",
            "tactic": "贴近木门起跳连斩破门；落入深坑后搜刮金币与矿脉；沿右上平台连续大跳向上攀爬登顶！"
        }
        self._is_busy = False
        self._init_clients()

    def _init_clients(self):
        if self.provider in ["openrouter", "openai_compatible"]:
            if HAS_OPENAI and self.api_key:
                try:
                    self.openai_client = OpenAI(
                        base_url=self.base_url if self.base_url else "https://api.openai.com/v1",
                        api_key=self.api_key,
                        timeout=15.0
                    )
                    print(f"[VLM Brain] OpenAI/OpenRouter Client active (Model: {self.model_name}, URL: {self.base_url}).")
                except Exception as e:
                    print(f"[VLM Brain] OpenAI init info: {e}")
        else:
            if HAS_GENAI and self.api_key:
                try:
                    self.gemini_client = genai.Client(api_key=self.api_key)
                    print(f"[VLM Brain] Gemini Native Client active ({self.model_name}).")
                except Exception as e:
                    print(f"[VLM Brain] Gemini init info: {e}")

    def _record_decision_log(self, data: dict, knight_pos: tuple):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = {
            "timestamp": now_str,
            "provider": self.provider,
            "model": self.model_name,
            "knight_pos": list(knight_pos),
            "decision": data
        }

        try:
            with open(self.jsonl_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        try:
            with open(self.text_log_path, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}] [{self.provider}/{self.model_name}] Pos:{knight_pos}\n")
                f.write(f"  - 阶段: {data.get('exploration_phase')} | 地形: {data.get('current_location')}\n")
                f.write(f"  - 目标: {data.get('macro_goal')}\n")
                f.write(f"  - 导航: 方向={data.get('direction')}, 垂直动作={data.get('vertical_action')}, 模式={data.get('navigation_mode')}\n")
                f.write(f"  - 战术: {data.get('tactic')}\n")
                f.write("-" * 75 + "\n")
        except Exception:
            pass

    def update_strategy_async(self, frame: np.ndarray, hud_info: dict, knight_pos: tuple = (0, 0)):
        now = time.time()
        if now < self.backoff_until:
            return

        current_hp = hud_info.get("health", 5)
        hp_dropped = (current_hp < self.last_known_health)
        self.last_known_health = current_hp

        time_elapsed = (now - self.last_query_time >= self.query_interval)
        if not (time_elapsed or hp_dropped):
            return
        if self._is_busy:
            return

        self.last_query_time = now
        self._is_busy = True
        thread = threading.Thread(target=self._query_worker, args=(frame.copy(), hud_info, knight_pos), daemon=True)
        thread.start()

    def _query_worker(self, frame: np.ndarray, hud_info: dict, knight_pos: tuple):
        try:
            h, w = frame.shape[:2]
            kx, ky = knight_pos
            rel_x = round(kx / max(w, 1), 2)
            rel_y = round(ky / max(h, 1), 2)

            small_frame = cv2.resize(frame, (640, 360))

            prompt = f"""
你是《空洞骑士》大师级 AI 攻略指挥官。当前小骑士位置为屏幕坐标 (X={rel_x}, Y={rel_y})。
请根据当前画面与位置，制定【全地图 100% 完整探索与立体通关攻略】：

《空洞骑士·国王山道》全地图 100% 探索路线树：
1. 【上层起始区】向右前进，遇爬虫斩杀，遇木门起跳挥刀斩碎 (JUMP_SLASH)。
2. 【深坑大跳崖】木门碎裂后走到右侧悬崖直接跳下深坑 (DROP_DOWN)。
3. 【下层洞穴区】
   - 向左探索：探索隐藏支线获取【亡者之怒】护符与吉欧宝箱；
   - 向右探索：击杀飞虫与爬虫，挥刀击碎发光的吉欧矿石爆金币 (MINE_GEO)。
4. 【向上阶梯攀登 (关键!)】向右上方向连续大跳 (JUMP_CLIMB_UP) 登上层层石阶平台，躲避刺坑并登顶。
5. 【出口大门】在最上方平台右侧斩碎出口大木门，向右进入德特茅斯小镇。

请根据小骑士当前位置与画面，判断所在阶段并输出严格 JSON 结构：
{{
  "current_location": "当前具体位置与地形描述",
  "exploration_phase": "PHASE_1_BARRIER 或 PHASE_2_DROP 或 PHASE_3_LOWER_CAVERN 或 PHASE_4_CLIMB_UP 或 PHASE_5_EXIT",
  "macro_goal": "当前宏观探索目标",
  "navigation_mode": "UPWARD_CLIMB 或 HORIZONTAL_EXPLORE 或 DROP_DOWN 或 MINE_AND_COLLECT 或 BACKTRACK",
  "direction": "RIGHT 或 LEFT",
  "vertical_action": "JUMP_CLIMB_UP 或 DROP_DOWN 或 NONE",
  "tactic": "具体的微操指引"
}}
"""
            data = None
            if self.openai_client:
                _, buffer = cv2.imencode(".jpg", small_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                b64_img = base64.b64encode(buffer).decode("utf-8")
                
                response = self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }
                    ],
                    temperature=0.2,
                    max_tokens=400
                )
                raw_text = response.choices[0].message.content
                data = extract_json_from_text(raw_text)

            elif self.gemini_client:
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                response = self.gemini_client.models.generate_content(
                    model=self.model_name,
                    contents=[pil_img, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                if response and response.text:
                    data = extract_json_from_text(response.text)

            if data:
                self.current_strategy = data
                self._record_decision_log(data, knight_pos)
                print(f"\n==========================================================================")
                print(f"  [{self.model_name} 动态指令已记录]")
                print(f"  - 地形/位置: {data.get('current_location')}")
                print(f"  - 阶段: {data.get('exploration_phase')} | 导航模式: {data.get('navigation_mode')}")
                print(f"  - 宏观目标: {data.get('macro_goal')}")
                print(f"  - 战术指令: {data.get('tactic')}")
                print(f"==========================================================================\n")

        except Exception as e:
            err_str = str(e)
            print(f"[VLM Brain Error] {err_str}")
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                self.backoff_until = time.time() + 20.0
        finally:
            self._is_busy = False

    def get_strategy(self) -> Dict[str, Any]:
        return self.current_strategy
