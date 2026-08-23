import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

def focus_hollow_knight():
    target_pids = set()
    for p in psutil.process_iter(['pid', 'name']):
        if "hollow" in p.info["name"].lower():
            target_pids.add(p.info["pid"])

    game_hwnds = []
    def enum_cb(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in target_pids:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if (rect.right - rect.left > 200) and (rect.bottom - rect.top > 200):
                game_hwnds.append(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    if game_hwnds:
        h = game_hwnds[0]
        user32.ShowWindow(h, 9) # SW_RESTORE
        user32.SetForegroundWindow(h)
        print(f"Focused game window HWND={h}")
        return True
    else:
        print("Game window not located yet.")
        return False

focus_hollow_knight()
