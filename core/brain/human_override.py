import time
import ctypes
import threading
import winsound
from typing import Optional, Dict, Any, Callable

user32 = ctypes.windll.user32

class HumanDirectiveOverride:
    """
    Human Strategic Directive Override System.
    Guarantees 100% immediate preemption of all LLM and local navigation states.
    Supports global hotkeys and F10 summonable text command bar.
    """
    def __init__(self, on_f10_callback: Optional[Callable] = None):
        self.is_active = False
        self.override_until = 0.0
        self.directive_name = ""
        self.override_strategy: Dict[str, Any] = {}
        self.on_f10_callback = on_f10_callback
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start_hotkey_listener(self):
        self._running = True
        self._thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def inject_directive(self, name: str, direction: str, nav_mode: str, vert_action: str = "NONE", tactic: str = "", duration: float = 15.0):
        now = time.time()
        self.is_active = True
        self.override_until = now + duration
        self.directive_name = name
        self.override_strategy = {
            "current_location": f"🚨 人工指令强制指定: [{name}]",
            "exploration_phase": "HUMAN_OVERRIDE_ACTIVE",
            "macro_goal": f"【人类插队指令】{name} (优先权高于大模型)",
            "navigation_mode": nav_mode,
            "direction": direction.upper(),
            "vertical_action": vert_action,
            "tactic": tactic if tactic else f"执行人类强制指令: 向 {direction.upper()} 推进，模式={nav_mode}"
        }
        try:
            winsound.Beep(900, 100)
            winsound.Beep(1200, 100)
        except Exception:
            pass
        print(f"\n==========================================================================")
        print(f"  [🚨 人工指令强制生效] 指令: {name} | 方向: {direction} | 持续: {duration}s")
        print(f"  (大模型与死胡同回溯已被彻底强行中断，小脑全力听从您的指挥！)")
        print(f"==========================================================================\n")

    def clear_override(self):
        if self.is_active:
            self.is_active = False
            self.override_until = 0.0
            self.directive_name = ""
            self.override_strategy = {}
            try:
                winsound.Beep(800, 120)
            except Exception:
                pass
            print(f"\n[🔄 人工指令已清除] 大模型自主决策权已恢复。\n")

    def get_active_override_strategy(self) -> Optional[Dict[str, Any]]:
        if self.is_active:
            now = time.time()
            if now < self.override_until:
                remain = round(self.override_until - now, 1)
                self.override_strategy["macro_goal"] = f"【人类插队指令】{self.directive_name} [剩余 {remain}s]"
                return self.override_strategy
            else:
                self.clear_override()
        return None

    def _hotkey_loop(self):
        VK_CONTROL = 0x11
        VK_LEFT = 0x25
        VK_UP = 0x26
        VK_RIGHT = 0x27
        VK_DOWN = 0x28
        VK_BACK = 0x08
        VK_NUMPAD0 = 0x60
        VK_F10 = 0x79

        while self._running:
            # 1. Global F10 Hotkey: Summon Text Command Bar
            if (user32.GetAsyncKeyState(VK_F10) & 0x8000) != 0:
                if self.on_f10_callback:
                    try:
                        self.on_f10_callback()
                    except Exception:
                        pass
                time.sleep(0.35)

            # 2. Ctrl + Directional Shortcuts
            ctrl_down = (user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0
            if ctrl_down:
                if (user32.GetAsyncKeyState(VK_LEFT) & 0x8000) != 0:
                    self.inject_directive("强制向左深度探索/回溯", "LEFT", "HORIZONTAL_EXPLORE", "NONE", "稳步向左侧探索隐藏支线与金币宝箱", 15.0)
                    time.sleep(0.35)

                elif (user32.GetAsyncKeyState(VK_RIGHT) & 0x8000) != 0:
                    self.inject_directive("强制向右破门主线推进", "RIGHT", "HORIZONTAL_EXPLORE", "NONE", "向右破门推进，消灭爬虫与障碍", 15.0)
                    time.sleep(0.35)

                elif (user32.GetAsyncKeyState(VK_UP) & 0x8000) != 0:
                    self.inject_directive("强制向上大跳攀登新阶梯", "RIGHT", "UPWARD_CLIMB", "JUMP_CLIMB_UP", "长蓄力连续大跳登上层层石阶平台", 15.0)
                    time.sleep(0.35)

                elif (user32.GetAsyncKeyState(VK_DOWN) & 0x8000) != 0:
                    self.inject_directive("强制向下跃下深坑探秘", "RIGHT", "DROP_DOWN", "DROP_DOWN", "走到悬崖边缘跳下深坑进入下层", 15.0)
                    time.sleep(0.35)

                elif ((user32.GetAsyncKeyState(VK_BACK) & 0x8000) != 0) or ((user32.GetAsyncKeyState(VK_NUMPAD0) & 0x8000) != 0):
                    self.clear_override()
                    time.sleep(0.35)

            time.sleep(0.02)
