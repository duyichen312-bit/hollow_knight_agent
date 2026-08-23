import ctypes
import time

user32 = ctypes.windll.user32
SendInput = user32.SendInput
MapVirtualKeyW = user32.MapVirtualKeyW

# Virtual Key constants
VK_CODES = {
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "a": 0x41,
    "d": 0x44,
    "w": 0x57,
    "s": 0x53,
    "z": 0x5A,
    "x": 0x58,
    "c": 0x43,
    "j": 0x4A,
    "k": 0x4B,
    "u": 0x55,
    "i": 0x49,
    "space": 0x20,
    "lshift": 0xA0
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

def win_send_key(vk_code: int, is_up: bool):
    scan = MapVirtualKeyW(vk_code, 0)
    flags = 0x0008 # KEYEVENTF_SCANCODE
    if vk_code in [0x25, 0x26, 0x27, 0x28]: # Extended arrow keys
        flags |= 0x0001 # KEYEVENTF_EXTENDEDKEY
    if is_up:
        flags |= 0x0002 # KEYEVENTF_KEYUP

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(vk_code, scan, flags, 0, ctypes.pointer(extra))
    inp = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

print("Virtual Key test function compiled successfully!")
