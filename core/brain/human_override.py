import time
import ctypes
import threading
import winsound
from typing import Optional, Dict, Any

user32 = ctypes.windll.user32

class HumanDirectiveOverride:
    """
    Human Strategic Directive Override System (人类战术指令强行插队/覆盖系统).
    Allows the human player to interrupt LLM strategy and force the local controller
    to execute high-priority human navigation & tactical instructions.
    """
    def __init__(self):
        self.is_active = False
        self.override_until = 0.0
        self.directive_name = ""
        self.override_strategy: Dict[str, Any] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start_hotkey_listener(self):
        self._running = True
        self._thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def inject_directive(self, name: str, direction: str, nav_mode: str, vert_action: str = "NONE", tactic: str = "", duration: float = 15.0):
        """
        Inject a high-priority human directive that overrides the LLM for `duration` seconds.
        """
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
            winsound.Beep(1100, 100)
        except Exception:
            pass
        print(f"\n==========================================================================")
        print(f"  [🚨 人工指令已插队生效] 指令: {name} | 方向: {direction} | 持续: {duration}s")
        print(f"  (大模型建议已被临时中断，本地小脑正优先执行您的战术！)")
        print(f"==========================================================================\n")

    def clear_override(self):
        """
        Clears the human override and returns full autonomy to the LLM.
        """
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
        """
        Listens for global override shortcuts:
        - Ctrl + Left: Force Left
        - Ctrl + Right: Force Right
        - Ctrl + Up: Force Upward Climb
        - Ctrl + Down: Force Downward Drop
        - Ctrl + Backspace / NumPad 0: Clear override
        """
        VK_CONTROL = 0x11
        VK_LEFT = 0x25
        VK_UP = 0x26
        VK_RIGHT = 0x27
        VK_DOWN = 0x28
        VK_BACK = 0x08
        VK_NUMPAD0 = 0x60

        while self._running:
            ctrl_down = (user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0

            if ctrl_down:
                # Ctrl + Up -> Force Upward Platform Climbing
                if user32.GetAsyncKeyState(VK_UP) & 0x0001:
                    self.inject_directive("向上大跳攀登新阶梯", "RIGHT", "UPWARD_CLIMB", "JUMP_CLIMB_UP", "长蓄力连续大跳登上层层石阶平台", 15.0)
                    time.sleep(0.3)

                # Ctrl + Left -> Force Left Deep Exploration
                elif user32.GetAsyncKeyState(VK_LEFT) & 0x0001:
                    self.inject_directive("向左深度探索/回溯", "LEFT", "HORIZONTAL_EXPLORE", "NONE", "稳步向左侧探索隐藏支线与金币宝箱", 15.0)
                    time.sleep(0.3)

                # Ctrl + Right -> Force Right Advance
                elif user32.GetAsyncKeyState(VK_RIGHT) & 0x0001:
                    self.inject_directive("向右破门主线推进", "RIGHT", "HORIZONTAL_EXPLORE", "NONE", "向右破门推进，消灭爬虫与障碍", 15.0)
                    time.sleep(0.3)

                # Ctrl + Down -> Force Downward Pit Drop
                elif user32.GetAsyncKeyState(VK_DOWN) & 0x0001:
                    self.inject_directive("向下跃下深坑探秘", "RIGHT", "DROP_DOWN", "DROP_DOWN", "走到悬崖边缘跳下深坑进入下层", 15.0)
                    time.sleep(0.3)

                # Ctrl + Backspace / NumPad 0 -> Clear Override
                elif (user32.GetAsyncKeyState(VK_BACK) & 0x0001) or (user32.GetAsyncKeyState(VK_NUMPAD0) & 0x0001):
                    self.clear_override()
                    time.sleep(0.3)

            time.sleep(0.02)
