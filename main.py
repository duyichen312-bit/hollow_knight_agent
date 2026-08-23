import os
import sys
import time
import yaml
import cv2
import win32gui
import win32process
import win32con
import psutil
import ctypes
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.capture import ScreenCapture
from core.perception.vision_pipeline import VisionPipeline
from core.ui.visual_debugger import VisualDebugger
from core.controller.gamepad import GameController
from core.brain.vlm_planner import VLMPlanner
from core.brain.state_machine import ReflexStateMachine

user32 = ctypes.windll.user32

def find_hollow_knight_hwnd():
    target_pids = set()
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if "hollow" in p.info["name"].lower():
                target_pids.add(p.info["pid"])
        except Exception:
            pass

    found = []
    def enum_cb(hwnd, extra):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in target_pids:
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2] - rect[0], rect[3] - rect[1]
                if w > 200 and h > 200:
                    found.append(hwnd)
        except Exception:
            pass
        return True

    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception:
        pass
    return found[0] if found else None

def force_focus_game(hwnd):
    if hwnd and user32.IsWindow(hwnd):
        try:
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.SwitchToThisWindow(hwnd, True)
        except Exception:
            pass

def main():
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    config_path = os.path.join(BASE_DIR, "configs", "config.yaml")
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    ui_cfg = config.get("vision", {}).get("ui", {})
    save_live_snapshot = ui_cfg.get("save_live_snapshot", True)

    game_hwnd = find_hollow_knight_hwnd()
    force_focus_game(game_hwnd)

    capture = ScreenCapture(window_title="Hollow Knight")
    vision = VisionPipeline(config=config.get("vision", {}))
    debugger = VisualDebugger(config=ui_cfg)
    controller = GameController(config=config.get("controls", {}), game_hwnd=game_hwnd)
    vlm_brain = VLMPlanner(config=config.get("brain", {}).get("llm", {}))
    state_machine = ReflexStateMachine(controller=controller, config=config.get("brain", {}).get("reflex", {}))

    last_fps_time = time.time()
    last_snapshot_time = 0.0
    frame_count = 0
    current_fps = 60.0

    try:
        while True:
            t0 = time.time()
            frame = capture.capture_frame()
            if frame is None:
                time.sleep(0.02)
                continue

            perception = vision.process(frame)

            hud_info = {
                "health": perception.hud.health,
                "max_health": perception.hud.max_health,
                "soul_ratio": perception.hud.soul_ratio,
                "is_alive": perception.hud.is_alive
            }
            kx, ky = perception.knight.center

            # Pass current player location to VLM brain for spatial guidance
            vlm_brain.update_strategy_async(frame, hud_info, knight_pos=(kx, ky))
            current_strategy = vlm_brain.get_strategy()

            # Execute 2D Metroidvania spatial action
            active_action = state_machine.step(perception, current_strategy)

            # FPS calculation
            frame_count += 1
            now = time.time()
            if now - last_fps_time >= 1.0:
                current_fps = frame_count / (now - last_fps_time)
                frame_count = 0
                last_fps_time = now

            if save_live_snapshot and (now - last_snapshot_time > 0.5):
                hud_display = debugger.draw_hud(
                    frame=frame,
                    perception=perception,
                    fps=current_fps,
                    strategy_info=current_strategy,
                    active_action=active_action
                )
                snapshot_path = os.path.join(BASE_DIR, "assets", "live_hud.jpg")
                cv2.imwrite(snapshot_path, hud_display)
                last_snapshot_time = now

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        controller.release_all()
        capture.close()

if __name__ == "__main__":
    main()
