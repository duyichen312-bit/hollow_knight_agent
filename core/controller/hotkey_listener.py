import time
import ctypes
import threading
import winsound
from typing import Optional, Callable
from core.controller.gamepad import GameController

user32 = ctypes.windll.user32

HOTKEY_VK_MAP = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "PAUSE": 0x13, "SCROLLLOCK": 0x91, "INSERT": 0x2D,
    "HOME": 0x24, "END": 0x23, "TAB": 0x09
}

class GlobalHotkeyManager:
    """
    Global Hotkey Manager for toggling between AI Control and Human Manual Control.
    Uses native Windows GetAsyncKeyState for lag-free, non-invasive global capture.
    """
    def __init__(self, controller: GameController, hotkey_name: str = "F9", on_toggle_cb: Optional[Callable[[bool], None]] = None):
        self.controller = controller
        self.hotkey_name = hotkey_name.upper()
        self.vk_code = HOTKEY_VK_MAP.get(self.hotkey_name, 0x78) # Default VK_F9
        self.on_toggle_cb = on_toggle_cb
        
        self.is_paused = False # False = AI Active, True = Human Manual Control
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[Hotkey Manager] 全局热键监听已就绪: 按 [{self.hotkey_name}] 随时切换 AI/人工接管。")

    def stop(self):
        self._running = False

    def toggle(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            # Human takes over: immediately release all active virtual keys
            self.controller.release_all()
            try:
                winsound.Beep(650, 140)
            except Exception:
                pass
            print(f"\n==========================================================================")
            print(f"  [⏸️ AI 控制已暂停] 🎮 人类已接管游戏控制！(按 [{self.hotkey_name}] 恢复 AI)")
            print(f"==========================================================================\n")
        else:
            # AI resumes
            try:
                winsound.Beep(1250, 140)
            except Exception:
                pass
            print(f"\n==========================================================================")
            print(f"  [▶️ AI 控制已恢复] 🤖 AI 重新接管游戏控制！(按 [{self.hotkey_name}] 暂停 AI)")
            print(f"==========================================================================\n")

        if self.on_toggle_cb:
            try:
                self.on_toggle_cb(self.is_paused)
            except Exception:
                pass

    def _loop(self):
        while self._running:
            # 0x8000 = key is currently down, 0x0001 = pressed since last call
            key_state = user32.GetAsyncKeyState(self.vk_code)
            if key_state & 0x0001 or (key_state & 0x8000 and (key_state & 0x0001)):
                self.toggle()
                time.sleep(0.3) # Debounce debounce
            time.sleep(0.02)
