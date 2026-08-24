import os
import time
import json
import ctypes
import threading
from typing import List, Dict, Any, Optional

user32 = ctypes.windll.user32

KEY_CODE_MAP = {
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "jump": 0x5A,   # 'z'
    "attack": 0x58, # 'x'
    "dash": 0x43,   # 'c'
    "focus": 0x41   # 'a'
}

class DemonstrationRecorder:
    """
    Human Expert Demonstration Recorder (人类专家操作示范录制器).
    Records human keystrokes, timings, and knight coordinate waypoints in real-time.
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.trajectories_dir = os.path.join(base_dir, "trajectories")
        os.makedirs(self.trajectories_dir, exist_ok=True)

        self.is_recording = False
        self.start_time = 0.0
        self.recorded_steps: List[Dict[str, Any]] = []
        self.current_knight_pos = (0.0, 0.0)
        self._thread: Optional[threading.Thread] = None

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        self.recorded_steps = []
        self._thread = threading.Thread(target=self._sampling_loop, daemon=True)
        self._thread.start()
        print(f"\n==========================================================================")
        print(f"  [🔴 开始录制人类操作示范] 您现在可以亲自玩游戏，AI 正在全程学习您的每一步操作！")
        print(f"  (操作完成后，再次按下 [F11] 或点击悬浮窗按钮即可保存为通关秘籍！)")
        print(f"==========================================================================\n")

    def stop_recording_and_save(self, trajectory_name: str = "expert_kings_pass") -> Optional[str]:
        if not self.is_recording:
            return None

        self.is_recording = False
        total_duration = round(time.time() - self.start_time, 2)
        
        # Summarize Waypoints
        waypoints = self._extract_key_waypoints(self.recorded_steps)
        
        trajectory_data = {
            "name": trajectory_name,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration_sec": total_duration,
            "total_raw_samples": len(self.recorded_steps),
            "waypoints": waypoints
        }

        save_path = os.path.join(self.trajectories_dir, f"{trajectory_name}.json")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dumps(trajectory_data, f, ensure_ascii=False, indent=2)
            # Write text version
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(trajectory_data, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[Recorder Error] {e}")

        print(f"\n==========================================================================")
        print(f"  [💾 人类示范录制完成] 耗时: {total_duration}s | 提炼关键路标点: {len(waypoints)} 个")
        print(f"  秘籍已保存至: trajectories/{trajectory_name}.json，AI 已成功习得该套路！")
        print(f"==========================================================================\n")
        return save_path

    def update_knight_pos(self, norm_kx: float, norm_ky: float):
        self.current_knight_pos = (norm_kx, norm_ky)

    def _sampling_loop(self):
        last_action = ""
        while self.is_recording:
            t = round(time.time() - self.start_time, 2)
            
            # Detect pressed keys
            pressed_keys = []
            for action_name, vk in KEY_CODE_MAP.items():
                if (user32.GetAsyncKeyState(vk) & 0x8000) != 0:
                    pressed_keys.append(action_name)

            if pressed_keys:
                kx, ky = self.current_knight_pos
                step_entry = {
                    "t": t,
                    "pos": [round(kx, 1), round(ky, 1)],
                    "keys": pressed_keys
                }
                self.recorded_steps.append(step_entry)

            time.sleep(0.05) # 20Hz sampling

    def _extract_key_waypoints(self, raw_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compresses 20Hz continuous keystrokes into clean human spatial waypoints.
        """
        if not raw_steps:
            return []

        waypoints = []
        last_wp_pos = (-999, -999)

        for step in raw_steps:
            kx, ky = step["pos"]
            keys = step["keys"]
            
            # Distance from last waypoint
            dist = ((kx - last_wp_pos[0])**2 + (ky - last_wp_pos[1])**2)**0.5
            
            # Significant actions (jump, dash, attack, or moved > 10% distance)
            is_special = any(k in keys for k in ["jump", "dash", "attack"])
            if dist > 8.0 or (is_special and dist > 3.0):
                action_desc = "MOVE_RIGHT"
                if "jump" in keys and "right" in keys:
                    action_desc = "JUMP_RIGHT_CLIMB"
                elif "jump" in keys and "left" in keys:
                    action_desc = "JUMP_LEFT_CLIMB"
                elif "jump" in keys:
                    action_desc = "JUMP_HIGH"
                elif "dash" in keys:
                    action_desc = "DASH_FORWARD"
                elif "attack" in keys:
                    action_desc = "SLASH_FORWARD"
                elif "left" in keys:
                    action_desc = "MOVE_LEFT"
                elif "right" in keys:
                    action_desc = "MOVE_RIGHT"

                wp = {
                    "waypoint_id": len(waypoints) + 1,
                    "t_sec": step["t"],
                    "pos": [kx, ky],
                    "expert_action": action_desc,
                    "keys": keys
                }
                waypoints.append(wp)
                last_wp_pos = (kx, ky)

        return waypoints
