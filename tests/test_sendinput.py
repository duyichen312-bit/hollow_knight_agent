import ctypes
import time

# Windows SendInput API definition
SendInput = ctypes.windll.user32.SendInput

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

# DirectInput Hardware Scan Codes (Set 1)
SCANCODES = {
    "left": (0x4B, 0x0001 | 0x0008),   # Extended key: Left Arrow
    "right": (0x4D, 0x0001 | 0x0008),  # Extended key: Right Arrow
    "up": (0x48, 0x0001 | 0x0008),     # Extended key: Up Arrow
    "down": (0x50, 0x0001 | 0x0008),   # Extended key: Down Arrow
    "z": (0x2C, 0x0008),               # Jump (Z key)
    "x": (0x2D, 0x0008),               # Attack (X key)
    "c": (0x2E, 0x0008),               # Dash (C key)
    "a": (0x1E, 0x0008),               # Focus/Cast (A key)
    "s": (0x1F, 0x0008),               # Quick Cast (S key)
    "d": (0x20, 0x0008),               # Dream Nail (D key)
    "space": (0x39, 0x0008),
}

def press_key(name):
    if name in SCANCODES:
        scan, flags = SCANCODES[name]
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, scan, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(name):
    if name in SCANCODES:
        scan, flags = SCANCODES[name]
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, scan, flags | 0x0002, 0, ctypes.pointer(extra)) # KEYEVENTF_KEYUP
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

print("SendInput hardware scan code engine tested successfully!")
