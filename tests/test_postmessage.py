import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

def get_hollow_knight_hwnd():
    target_pids = set()
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if "hollow" in p.info["name"].lower():
                target_pids.add(p.info["pid"])
        except Exception:
            pass

    found = []
    def enum_cb(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in target_pids:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            if w > 200 and h > 200:
                found.append(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return found[0] if found else None

hwnd = get_hollow_knight_hwnd()
print("Found Game HWND:", hwnd)
