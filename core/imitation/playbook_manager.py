import os
import json
from typing import Dict, Any, List, Optional

class PlaybookManager:
    """
    Expert Demonstration Playbook Manager (专家通关秘籍与示范轨迹管理器).
    Stores human demonstration trajectories and formats them for VLM Few-shot guidance
    and local autonomous trajectory following.
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.trajectories_dir = os.path.join(base_dir, "trajectories")
        os.makedirs(self.trajectories_dir, exist_ok=True)
        self.active_playbook_name = "expert_kings_pass"
        self._ensure_default_expert_playbook()

    def _ensure_default_expert_playbook(self):
        default_path = os.path.join(self.trajectories_dir, "expert_kings_pass.json")
        if not os.path.exists(default_path):
            golden_playbook = {
                "name": "expert_kings_pass",
                "stage": "国王山道 (King\'s Pass)",
                "author": "人类高玩/专家示范",
                "description": "国王山道 100% 满分通关示范：破门跳崖 -> 搜刮矿石 -> 中央大跳起跳 -> 连跃3层悬空石台 -> 冲刺登顶斩门！",
                "waypoints": [
                    {"id": 1, "pos": [20.0, 38.0], "action": "MOVE_RIGHT", "desc": "上层走廊向右平稳推进"},
                    {"id": 2, "pos": [55.0, 38.0], "action": "SLASH_FORWARD", "desc": "贴近初始木门起跳连斩破门"},
                    {"id": 3, "pos": [85.0, 38.0], "action": "DROP_DOWN", "desc": "走到悬崖边缘跳下深坑进入下层"},
                    {"id": 4, "pos": [35.0, 68.0], "action": "MOVE_RIGHT", "desc": "下层地面向右收集吉欧矿石与金币"},
                    {"id": 5, "pos": [50.0, 68.0], "action": "JUMP_CLIMB_UP", "desc": "关键起跳点！必须向上大跳(长按跳跃0.4s)登上第1悬空台 [50, 52]"},
                    {"id": 6, "pos": [50.0, 52.0], "action": "JUMP_RIGHT", "desc": "站稳第1台，向右上跳跃登上第2悬空台 [65, 40]"},
                    {"id": 7, "pos": [65.0, 40.0], "action": "JUMP_LEFT", "desc": "站稳第2台，向左上方高跳登上第3高位石台 [50, 28]"},
                    {"id": 8, "pos": [50.0, 28.0], "action": "JUMP_RIGHT_DASH", "desc": "高位石台向右大跳配合空中冲刺，登上顶层出口 [85, 25]"},
                    {"id": 9, "pos": [85.0, 25.0], "action": "SLASH_FORWARD", "desc": "抵达出口大木门，起跳挥刀斩裂大门进入德特茅斯小镇通关！"}
                ]
            }
            try:
                with open(default_path, "w", encoding="utf-8") as f:
                    json.dump(golden_playbook, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    def get_playbook(self, name: str = "expert_kings_pass") -> Dict[str, Any]:
        path = os.path.join(self.trajectories_dir, f"{name}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_closest_expert_waypoint(self, norm_x: float, norm_y: float) -> Optional[Dict[str, Any]]:
        playbook = self.get_playbook(self.active_playbook_name)
        waypoints = playbook.get("waypoints", [])
        if not waypoints:
            return None

        best_wp = None
        min_dist = float("inf")
        for wp in waypoints:
            wx, wy = wp.get("pos", [0, 0])
            dist = ((norm_x - wx)**2 + (norm_y - wy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                best_wp = wp

        return best_wp

    def format_playbook_prompt(self) -> str:
        playbook = self.get_playbook(self.active_playbook_name)
        waypoints = playbook.get("waypoints", [])
        if not waypoints:
            return "暂无人类示范记录。"

        lines = [
            f"【人类专家实操通关轨迹秘籍 (Expert Demonstration Playbook)】:",
            f"示范关卡: {playbook.get('stage', '国王山道')} | 核心心法: {playbook.get('description', '')}"
        ]
        for wp in waypoints:
            lines.append(f"  * 路标{wp.get('id', '?')}: 网格目标 {wp.get('pos')} -> 专家动作: {wp.get('action')} ({wp.get('desc', '')})")

        return "\n".join(lines)
