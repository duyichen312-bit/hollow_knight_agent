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
from core.perception.grid_annotator import VisualGridAnnotator
from core.brain.action_history_buffer import ActionHistoryBuffer
from core.brain.stage_map_knowledge import StageMapKnowledge
from core.brain.topological_navigator import TopologicalPlatformNavigator
from core.imitation.playbook_manager import PlaybookManager

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
    Spatial ReAct Multimodal Brain with Human Demonstration Learning & Topological Navigator.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Profile Manager
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

        # Short-term Action Memory Buffer (3 steps)
        self.history_buffer = ActionHistoryBuffer(max_size=3)
        # Topological Platform Navigator
        self.topo_nav = TopologicalPlatformNavigator()
        # Human Demonstration Playbook Manager
        self.playbook_mgr = PlaybookManager(self.base_dir)

        # Logs Directory
        self.logs_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.jsonl_log_path = os.path.join(self.logs_dir, "vlm_decisions.jsonl")
        self.text_log_path = os.path.join(self.logs_dir, "vlm_journal.log")

        # Current Spatial ReAct Strategy
        self.current_strategy: Dict[str, Any] = {
            "current_stage": "国王山道 (King\'s Pass)",
            "current_zone": "ZONE_A_UPPER_START (上层起始走廊)",
            "scene_analysis": "小骑士位于初始区域，右侧有石阶平台与木门",
            "threat_level": "LOW",
            "action": "MOVE_RIGHT",
            "target_coords": [60, 60],
            "duration_ms": 600,
            "reasoning": "向前稳步探索并清理沿途障碍",
            # Backward compatibility fields
            "current_location": "国王山道 (King\'s Pass)",
            "exploration_phase": "PHASE_1_BARRIER",
            "macro_goal": "稳步向右推进，遇到木门起跳连斩",
            "navigation_mode": "HORIZONTAL_EXPLORE",
            "direction": "RIGHT",
            "vertical_action": "NONE",
            "tactic": "向右稳步探索"
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
                    print(f"[VLM Brain] OpenAI/OpenRouter Client active ({self.model_name}).")
                except Exception as e:
                    print(f"[VLM Brain] OpenAI init error: {e}")
        else:
            if HAS_GENAI and self.api_key:
                try:
                    self.gemini_client = genai.Client(api_key=self.api_key)
                    print(f"[VLM Brain] Gemini Native Client active ({self.model_name}).")
                except Exception as e:
                    print(f"[VLM Brain] Gemini init error: {e}")

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
                f.write(f"  - 关卡与分区: {data.get('current_stage')} | {data.get('current_zone')}\n")
                f.write(f"  - 态势剖析: {data.get('scene_analysis')}\n")
                f.write(f"  - 决策动作: {data.get('action')} | 目标落点: {data.get('target_coords')} | 耗时: {data.get('duration_ms')}ms | 威胁: {data.get('threat_level')}\n")
                f.write(f"  - 推理依据: {data.get('reasoning')}\n")
                f.write("-" * 80 + "\n")
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
            norm_kx = round((kx / max(w, 1)) * 100, 1)
            norm_ky = round((ky / max(h, 1)) * 100, 1)

            # Stage 1: Visual Prompting & Grid Overlay
            annotated_frame = VisualGridAnnotator.annotate(frame, target_width=768, knight_norm_pos=(norm_kx, norm_ky))

            # Save annotated image for visual inspection
            try:
                grid_debug_path = os.path.join(self.base_dir, "assets", "vlm_input_grid.jpg")
                cv2.imwrite(grid_debug_path, annotated_frame)
            except Exception:
                pass

            # Stage 2: Topological Graph Planning & Human Expert Playbook
            topo_plan = self.topo_nav.plan_next_topological_action(norm_kx, norm_ky)
            stage_knowledge = StageMapKnowledge.get_stage_prompt_context("KINGS_PASS")
            current_subzone = StageMapKnowledge.identify_zone("KINGS_PASS", norm_kx, norm_ky)
            playbook_text = self.playbook_mgr.format_playbook_prompt()

            # Stage 3: Action Context Buffer (Recent 3 steps)
            history_text = self.history_buffer.format_history_prompt()

            # Stage 4: ReAct Framework Prompt with Demonstration Learning
            prompt = f"""
你是一名具备顶级空间几何、关卡拓扑与人类专家示范学习能力的《空洞骑士》多模态 ReAct 决策大脑。
输入图片已叠加 0~100 归一化绿色坐标网格标尺（左上角为(0,0)，右下角为(100,100)）。

{stage_knowledge}

{playbook_text}

【拓扑路网导航系统推荐路径】:
- 当前所在平台: {topo_plan['current_node']} ➔ 目标下一平台: {topo_plan['target_node']}
- 推荐动作: {topo_plan['action']} (目标网格 {topo_plan['target_coords']})

【小骑士当前精准地标与区域定位】:
- 当前网格坐标: X={norm_kx}, Y={norm_ky}
- 判定所处分区: {current_subzone['name']} ({current_subzone['zone_id']})
- 避坑严重警告: {current_subzone['danger_notes']}

【历史动作时序记忆 (最近 3 步)】:
{history_text}

【当前小骑士状态】:
- 生命值 (HP): {hud_info.get('health', 5)} / {hud_info.get('max_health', 5)}

【对齐人类专家示范行为】:
1. 严格对照【人类专家实操通关轨迹秘籍】，学习人类专家在当前坐标下的跳跃与攀登决策！
2. ⚠️ 若处于下层右侧 (X>=68, Y>=55)，右侧为绝对封死死胡同，必须向左折返至中央起跳点向上大跳攀登悬空石阶！

【支持 action 动作代码库】:
- "MOVE_RIGHT" / "MOVE_LEFT" (地面稳步探索移动)
- "JUMP_RIGHT" / "JUMP_LEFT" (向斜上方跳跃登上新石阶平台)
- "JUMP_RIGHT_DASH" / "JUMP_LEFT_DASH" (大跳配合空中冲刺跨越宽断崖/刺坑)
- "JUMP_CLIMB_UP" (向上连续大跳攀爬多层悬空石阶登顶)
- "DROP_DOWN" (走到悬崖边缘跳下深坑进入下层洞穴)
- "SLASH_FORWARD" (贴近障碍木门或怪物正面快速连斩)
- "POGO_DOWN" (空中下劈借力弹跳)
- "FOCUS_HEAL" (在安全死角原地回血)
- "RETREAT_BACKTRACK" (遭遇不可逾越死墙，掉头向反方向回溯脱困)

【输出规范】:
请严格输出标准 JSON 格式（严禁包含任何其他文字）：
{{
  "current_stage": "国王山道 (King\'s Pass) - 序章第一关",
  "current_zone": "当前所在分区名称与ID",
  "scene_analysis": "简述小骑士当前网格坐标、周围障碍物/尖刺坐标、平台及出口分布",
  "threat_level": "LOW 或 MEDIUM 或 HIGH 或 CRITICAL",
  "action": "上述动作代码之一",
  "target_coords": [50, 52],
  "duration_ms": 600,
  "reasoning": "基于人类专家示范秘籍与关卡拓扑推理出的详细战术决策理由"
}}
"""
            data = None
            if self.openai_client:
                _, buffer = cv2.imencode(".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
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
                    max_tokens=450
                )
                raw_text = response.choices[0].message.content
                data = extract_json_from_text(raw_text)

            elif self.gemini_client:
                rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
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

            if not data or "action" not in data:
                data = {
                    "current_stage": "国王山道 (King\'s Pass)",
                    "current_zone": current_subzone['name'],
                    "scene_analysis": f"拓扑导航器接管 (坐标 {norm_kx}, {norm_ky})",
                    "threat_level": "LOW",
                    "action": topo_plan["action"],
                    "target_coords": topo_plan["target_coords"],
                    "duration_ms": topo_plan["duration_ms"],
                    "reasoning": topo_plan["reasoning"]
                }

            # Dead-End Safety Filter: Overrule MOVE_RIGHT on Dead End Node
            if (norm_kx >= 68.0 and norm_ky >= 55.0) and "RIGHT" in data.get("action", ""):
                data["action"] = "JUMP_LEFT"
                data["target_coords"] = [50, 52]
                data["reasoning"] = "[对齐专家秘籍] 处于右侧死胡同盲区，向左折返跃上中央悬空石阶！"

            act = data.get("action", "MOVE_RIGHT")
            data["current_location"] = f"{data.get('current_stage', '国王山道')} | {data.get('current_zone', '探索区')}"
            data["macro_goal"] = data.get("reasoning", "")
            data["tactic"] = f"{act} ➔ 目标点 {data.get('target_coords', [0,0])} ({data.get('duration_ms', 400)}ms)"

            if "RIGHT" in act:
                data["direction"] = "RIGHT"
            elif "LEFT" in act or "RETREAT" in act:
                data["direction"] = "LEFT"
            else:
                data["direction"] = "RIGHT"

            if "CLIMB" in act or "JUMP" in act:
                data["navigation_mode"] = "UPWARD_CLIMB"
                data["vertical_action"] = "JUMP_CLIMB_UP"
            elif "DROP" in act:
                data["navigation_mode"] = "DROP_DOWN"
                data["vertical_action"] = "DROP_DOWN"
            else:
                data["navigation_mode"] = "HORIZONTAL_EXPLORE"
                data["vertical_action"] = "NONE"

            self.current_strategy = data
            self.history_buffer.add_step(data, (norm_kx, norm_ky), hud_info.get("health", 5))
            self._record_decision_log(data, (norm_kx, norm_ky))

            print(f"\n==========================================================================")
            print(f"  [🎓 专家秘籍学习对齐] {data.get('current_stage')} | {data.get('current_zone')}")
            print(f"  - 坐标: ({norm_kx}, {norm_ky}) | 动作: {data.get('action')} ➔ 目标: {data.get('target_coords')}")
            print(f"  - 推理依据: {data.get('reasoning')}")
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
