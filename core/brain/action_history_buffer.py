import time
from typing import List, Dict, Any, Optional

class ActionHistoryBuffer:
    """
    Action Context Buffer (短期动作与时序记忆缓冲池).
    Maintains a rolling window of recent decisions and their real-world outcome feedback,
    preventing circular stagnation and repetitive invalid path trials.
    """
    def __init__(self, max_size: int = 3):
        self.max_size = max_size
        self.buffer: List[Dict[str, Any]] = []
        self.last_pos = (0, 0)
        self.last_hp = 5

    def add_step(self, action_dict: Dict[str, Any], current_pos_norm: tuple, current_hp: int):
        now_str = time.strftime("%H:%M:%S")
        kx, ky = current_pos_norm
        last_kx, last_ky = self.last_pos

        # Compute feedback for the PREVIOUS step in buffer
        if self.buffer:
            last_entry = self.buffer[-1]
            last_act = last_entry.get("action", "")
            dx = kx - last_kx
            dy = ky - last_ky

            feedback_parts = []
            if current_hp < self.last_hp:
                feedback_parts.append(f"受击扣血(HP {self.last_hp}->{current_hp})")
            
            if "MOVE" in last_act or "SLASH" in last_act:
                if abs(dx) < 2 and abs(dy) < 2:
                    feedback_parts.append(f"撞墙或遇障碍阻挡，小骑士坐标停滞在({int(kx)},{int(ky)})")
                else:
                    feedback_parts.append(f"位移成功，小骑士到达({int(kx)},{int(ky)})")
            elif "JUMP" in last_act or "DASH" in last_act:
                feedback_parts.append(f"跳跃/冲刺完成，当前落点在({int(kx)},{int(ky)})")
            else:
                feedback_parts.append(f"动作完成，当前坐标在({int(kx)},{int(ky)})")

            last_entry["feedback"] = "；".join(feedback_parts)

        # Append new step
        entry = {
            "timestamp": now_str,
            "scene_analysis": action_dict.get("scene_analysis", ""),
            "action": action_dict.get("action", "MOVE_RIGHT"),
            "target_coords": action_dict.get("target_coords", [0, 0]),
            "duration_ms": action_dict.get("duration_ms", 400),
            "reasoning": action_dict.get("reasoning", ""),
            "feedback": "正在执行中..."
        }

        self.buffer.append(entry)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

        self.last_pos = (kx, ky)
        self.last_hp = current_hp

    def format_history_prompt(self) -> str:
        if not self.buffer:
            return "暂无历史动作记录（初次启动）。"

        lines = []
        for i, step in enumerate(self.buffer):
            step_idx = len(self.buffer) - i
            label = "上一步" if step_idx == 1 else (f"前{step_idx}步")
            act = step.get("action", "NONE")
            target = step.get("target_coords", [0, 0])
            feedback = step.get("feedback", "执行完成")
            lines.append(f"- [{label}] 决策动作: {act} | 目标坐标: {target} -> 执行反馈: {feedback}")
        
        return "\n".join(lines)
