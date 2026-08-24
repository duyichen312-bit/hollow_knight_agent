import os
import sys
import time
import yaml
import cv2
import traceback
import win32gui
import win32process
import win32con
import psutil
import ctypes
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.capture import ScreenCapture
from core.perception.vision_pipeline import VisionPipeline
from core.ui.visual_debugger import VisualDebugger
from core.ui.floating_overlay import FloatingOverlay
from core.controller.gamepad import GameController
from core.controller.hotkey_listener import GlobalHotkeyManager
from core.brain.human_override import HumanDirectiveOverride
from core.brain.vlm_planner import VLMPlanner
from core.brain.state_machine import ReflexStateMachine

user32 = ctypes.windll.user32

def log_crash_error(err_msg: str):
    try:
        logs_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        crash_file = os.path.join(logs_dir, "crash_dump.log")
        with open(crash_file, "a", encoding="utf-8") as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] CRASH DUMP:\n")
            f.write(err_msg + "\n" + "="*80 + "\n")
    except Exception:
        pass

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
    try:
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        config_path = os.path.join(BASE_DIR, "configs", "config.yaml")
        
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8-sig") as f:
                    config = yaml.safe_load(f) or {}
            except Exception:
                pass

        ui_cfg = config.get("vision", {}).get("ui", {})
        save_live_snapshot = ui_cfg.get("save_live_snapshot", True)
        enable_overlay = ui_cfg.get("enable_floating_overlay", True)
        hotkey_name = config.get("controls", {}).get("toggle_ai_hotkey", "F9")

        # 1. Attach and Force-Focus Game Window
        game_hwnd = find_hollow_knight_hwnd()
        force_focus_game(game_hwnd)

        capture = ScreenCapture(window_title="Hollow Knight")
        vision = VisionPipeline(config=config.get("vision", {}))
        debugger = VisualDebugger(config=ui_cfg)
        controller = GameController(config=config.get("controls", {}), game_hwnd=game_hwnd)
        
        # 2. Global Hotkey Manager (F9)
        hotkey_mgr = GlobalHotkeyManager(controller=controller, hotkey_name=hotkey_name)
        hotkey_mgr.start()

        # 3. Typing State Tracking
        is_typing_command = False

        def on_typing_state_change(typing: bool):
            nonlocal is_typing_command
            is_typing_command = typing
            if typing:
                controller.release_all()

        # 4. Floating Overlay Forward Declaration
        overlay = None

        # 5. Human Strategic Override System with F10 Hotkey
        def on_f10_press():
            if overlay:
                overlay.summon_text_command_box()

        human_override = HumanDirectiveOverride(on_f10_callback=on_f10_press)
        human_override.start_hotkey_listener()

        # 6. Floating HUD Callback for Buttons & Text Input
        def on_overlay_override_click(action_type: str, custom_data: Optional[dict] = None):
            if action_type == "CUSTOM_TEXT_PLAN" and custom_data:
                human_override.inject_directive(
                    name=custom_data.get("name", "文字指令"),
                    direction=custom_data.get("direction", "RIGHT"),
                    nav_mode=custom_data.get("navigation_mode", "HORIZONTAL_EXPLORE"),
                    vert_action=custom_data.get("vertical_action", "NONE"),
                    tactic=custom_data.get("tactic", ""),
                    duration=custom_data.get("duration", 15.0)
                )
            elif action_type == "CLIMB_UP":
                human_override.inject_directive("强制向上大跳攀登新阶梯", "RIGHT", "UPWARD_CLIMB", "JUMP_CLIMB_UP", "长蓄力连续大跳登上层层石阶平台", 15.0)
            elif action_type == "FORCE_LEFT":
                human_override.inject_directive("强制向左深度探索/回溯", "LEFT", "HORIZONTAL_EXPLORE", "NONE", "稳步向左侧探索隐藏支线与金币宝箱", 15.0)
            elif action_type == "FORCE_RIGHT":
                human_override.inject_directive("强制向右破门主线推进", "RIGHT", "HORIZONTAL_EXPLORE", "NONE", "向右破门推进，消灭爬虫与障碍", 15.0)
            elif action_type == "DROP_DOWN":
                human_override.inject_directive("向下跃下深坑探秘", "RIGHT", "DROP_DOWN", "DROP_DOWN", "走到悬崖边缘跳下深坑进入下层", 15.0)
            elif action_type == "CLEAR_OVERRIDE":
                human_override.clear_override()

        if enable_overlay:
            overlay = FloatingOverlay(
                on_override_cb=on_overlay_override_click,
                on_typing_state_cb=on_typing_state_change,
                game_hwnd=game_hwnd
            )
            overlay.start()

        vlm_brain = VLMPlanner(config=config.get("brain", {}).get("llm", {}))
        state_machine = ReflexStateMachine(controller=controller, config=config.get("brain", {}).get("reflex", {}))

        last_fps_time = time.time()
        last_snapshot_time = 0.0
        frame_count = 0
        current_fps = 60.0

        while True:
            try:
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

                # VLM Background Strategy Planner
                vlm_brain.update_strategy_async(frame, hud_info, knight_pos=(kx, ky))
                vlm_strategy = vlm_brain.get_strategy()

                # Priority 1: Check Human Directive Override
                override_strat = human_override.get_active_override_strategy()
                if override_strat:
                    effective_strategy = override_strat
                    is_override = True
                else:
                    effective_strategy = vlm_strategy
                    is_override = False

                # Update Floating Overlay HUD in real time
                if overlay:
                    overlay.update_vlm_strategy(effective_strategy, provider_name=vlm_brain.model_name, is_human_override=is_override)
                    overlay.update_control_status(is_paused=hotkey_mgr.is_paused, hotkey=hotkey_name, fps=current_fps)

                # Execution state branch:
                if is_typing_command:
                    active_action = "TYPING_COMMAND (PAUSED)"
                elif hotkey_mgr.is_paused:
                    active_action = f"MANUAL_CONTROL (Press {hotkey_name} to Resume)"
                else:
                    active_action = state_machine.step(perception, effective_strategy)

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
                        strategy_info=effective_strategy,
                        active_action=active_action
                    )
                    snapshot_path = os.path.join(BASE_DIR, "assets", "live_hud.jpg")
                    cv2.imwrite(snapshot_path, hud_display)
                    last_snapshot_time = now

                time.sleep(0.01)

            except Exception as frame_err:
                # Per-frame self-healing protection
                log_crash_error(f"Per-frame error: {frame_err}\n{traceback.format_exc()}")
                time.sleep(0.05)

    except Exception as e:
        log_crash_error(f"Fatal main loop crash: {e}\n{traceback.format_exc()}")
    finally:
        try:
            if overlay:
                overlay.stop()
            human_override.stop()
            hotkey_mgr.stop()
            controller.release_all()
            capture.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
