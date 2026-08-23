import ctypes
from ctypes import wintypes
import time
import threading
from typing import Optional, Set

user32 = ctypes.windll.user32
SendInput = user32.SendInput
MapVirtualKeyW = user32.MapVirtualKeyW
PostMessageW = user32.PostMessageW

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# Direct Mapping to both Hollow Knight layout schemes (Arrow+ZXC & WASD+JK)
ACTION_VKS = {
    "right": [0x27, 0x44],        # Right Arrow + D key
    "left":  [0x25, 0x41],        # Left Arrow + A key
    "up":    [0x26, 0x57],        # Up Arrow + W key
    "down":  [0x28, 0x53],        # Down Arrow + S key
    "jump":  [0x5A, 0x20],        # Z key + Spacebar
    "attack":[0x58, 0x4A],        # X key + J key
    "dash":  [0x43, 0x4B, 0x10],  # C key + K key + Left Shift
    "focus": [0x41, 0x55],        # A key + U key
    "cast":  [0x53, 0x49]         # S key + I key
}

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class GameController:
    """
    Hardware-level DirectInput Gamepad & Keyboard Emulation for Hollow Knight.
    Provides precise, reliable micro-maneuvers for 60Hz Reflex State Machine.
    """
    def __init__(self, config: dict = None, game_hwnd: Optional[int] = None):
        self.config = config or {}
        self.game_hwnd = game_hwnd
        self.current_movement: Optional[str] = None
        self.active_vks: Set[int] = set()
        self._lock = threading.Lock()

    def set_game_hwnd(self, hwnd: int):
        self.game_hwnd = hwnd

    def _send_vk(self, vk: int, is_up: bool):
        scan = MapVirtualKeyW(vk, 0)
        flags = 0x0008 # KEYEVENTF_SCANCODE
        if vk in [0x25, 0x26, 0x27, 0x28]: # Extended arrow keys
            flags |= 0x0001
        if is_up:
            flags |= 0x0002 # KEYEVENTF_KEYUP

        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(vk, scan, flags, 0, ctypes.pointer(extra))
        inp = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

        if self.game_hwnd and user32.IsWindow(self.game_hwnd):
            msg = WM_KEYUP if is_up else WM_KEYDOWN
            lParam = 1 | (scan << 16)
            if is_up:
                lParam |= (1 << 30) | (1 << 31)
            PostMessageW(self.game_hwnd, msg, vk, lParam)

    def _press_action(self, action: str):
        vks = ACTION_VKS.get(action, [])
        for vk in vks:
            if vk not in self.active_vks:
                self._send_vk(vk, is_up=False)
                self.active_vks.add(vk)

    def _release_action(self, action: str):
        vks = ACTION_VKS.get(action, [])
        for vk in vks:
            if vk in self.active_vks:
                self._send_vk(vk, is_up=True)
                self.active_vks.discard(vk)

    def set_movement(self, direction: Optional[str]):
        with self._lock:
            if direction == self.current_movement:
                return
            if self.current_movement:
                self._release_action(self.current_movement)
            if direction in ["left", "right"]:
                self._press_action(direction)
                self.current_movement = direction
            else:
                self.current_movement = None

    def tap_jump(self, duration: float = 0.32):
        def _worker():
            with self._lock:
                self._press_action("jump")
            time.sleep(duration)
            with self._lock:
                self._release_action("jump")
        threading.Thread(target=_worker, daemon=True).start()

    def tap_attack(self, duration: float = 0.08):
        def _worker():
            with self._lock:
                self._press_action("attack")
            time.sleep(duration)
            with self._lock:
                self._release_action("attack")
        threading.Thread(target=_worker, daemon=True).start()

    def jump_and_slash(self, direction: str = "right", repeats: int = 3):
        """
        High Jump + Mid-Air Nail Slash Combo (Essential for breaking wooden doors & climbing ledges).
        """
        def _worker():
            self.set_movement(direction)
            # High jump
            with self._lock:
                self._press_action("jump")
            time.sleep(0.12)
            # Mid-air slashes
            for _ in range(repeats):
                with self._lock:
                    self._press_action("attack")
                time.sleep(0.08)
                with self._lock:
                    self._release_action("attack")
                time.sleep(0.08)
            with self._lock:
                self._release_action("jump")
        threading.Thread(target=_worker, daemon=True).start()

    def combo_slashes(self, direction: str = "right", count: int = 3):
        """
        Ground nail slash combo.
        """
        def _worker():
            self.set_movement(direction)
            for _ in range(count):
                with self._lock:
                    self._press_action("attack")
                time.sleep(0.08)
                with self._lock:
                    self._release_action("attack")
                time.sleep(0.10)
        threading.Thread(target=_worker, daemon=True).start()

    def pogo_slash(self):
        """
        Aerial Downward Pogo Slash.
        """
        def _worker():
            with self._lock:
                self._press_action("down")
            time.sleep(0.03)
            with self._lock:
                self._press_action("attack")
            time.sleep(0.09)
            with self._lock:
                self._release_action("attack")
                self._release_action("down")
        threading.Thread(target=_worker, daemon=True).start()

    def dash_evade(self, direction: str = "left"):
        """
        Emergency dash retreat.
        """
        def _worker():
            self.set_movement(direction)
            time.sleep(0.03)
            with self._lock:
                self._press_action("dash")
            time.sleep(0.08)
            with self._lock:
                self._release_action("dash")
        threading.Thread(target=_worker, daemon=True).start()

    def release_all(self):
        with self._lock:
            for vk in list(self.active_vks):
                self._send_vk(vk, is_up=True)
            self.active_vks.clear()
            self.current_movement = None
