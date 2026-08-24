import re
from typing import Dict, Any

class TextCommandParser:
    """
    Intelligent Natural Language Text Command Parser (自然语言文字战术指令解析器).
    Translates free-form Chinese and English game commands into executable 2D Metroidvania directive plans.
    """
    @staticmethod
    def parse_command(user_text: str) -> Dict[str, Any]:
        text = user_text.strip().lower()
        if not text:
            return {}

        # 1. Extract Duration (e.g., "5秒", "10s", "20 秒")
        duration = 15.0 # Default 15 seconds
        match_time = re.search(r"(\d+)\s*(?:秒|s|sec)", text)
        if match_time:
            try:
                duration = float(match_time.group(1))
                duration = max(3.0, min(60.0, duration))
            except Exception:
                pass

        # 2. Extract Primary Direction
        direction = "RIGHT"
        if any(w in text for w in ["左", "left", "回溯", "倒退", "后退", "往回"]):
            direction = "LEFT"
        elif any(w in text for w in ["右", "right", "前进", "往前", "向前"]):
            direction = "RIGHT"

        # 3. Extract Navigation & Vertical Mode
        nav_mode = "HORIZONTAL_EXPLORE"
        vert_action = "NONE"

        # Upward climbing / jumping
        if any(w in text for w in ["上", "跳", "爬", "登顶", "台阶", "平台", "高处", "jump", "climb", "up"]):
            nav_mode = "UPWARD_CLIMB"
            vert_action = "JUMP_CLIMB_UP"

        # Downward pit drop
        elif any(w in text for w in ["下", "深坑", "坑", "跳下", "落", "drop", "down", "pit"]):
            nav_mode = "DROP_DOWN"
            vert_action = "DROP_DOWN"

        # Mining / Barrier break
        elif any(w in text for w in ["破门", "打门", "砍门", "采矿", "矿石", "连斩", "slash", "mine", "break"]):
            nav_mode = "MINE_AND_COLLECT"
            vert_action = "JUMP_CLIMB_UP"

        return {
            "name": f"文字指令: {user_text}",
            "direction": direction,
            "navigation_mode": nav_mode,
            "vertical_action": vert_action,
            "duration": duration,
            "tactic": f"执行文字指令: {user_text} (方向={direction}, 模式={nav_mode})"
        }
