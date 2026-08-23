import ctypes
import time
import psutil

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

console_hwnd = kernel32.GetConsoleWindow()
print("Console HWND:", console_hwnd)

# Find Hollow Knight
game_hwnd = None
target_pids = set()
for p in psutil.process_iter(['pid', 'name']):
    try:
        if "hollow" in p.info["name"].lower():
            target_pids.add(p.info["pid"])
    except Exception:
        pass

def enum_cb(hwnd, lparam):
    global game_hwnd
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in target_pids:
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w > 400 and h > 300:
            game_hwnd = hwnd
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
print("Detected Game HWND:", game_hwnd)
