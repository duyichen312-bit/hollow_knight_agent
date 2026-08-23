import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

target_pids = set()
for p in psutil.process_iter(['pid', 'name']):
    if "hollow" in p.info["name"].lower():
        target_pids.add(p.info["pid"])
print("Target Hollow Knight PIDs:", target_pids)

game_hwnds = []

def enum_windows_callback(hwnd, lparam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in target_pids:
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        title = buf.value

        buf_cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf_cls, 256)
        cls = buf_cls.value
        
        print(f"Found Game HWND={hwnd}, Title={title!r}, Class={cls!r}, Rect=({rect.left},{rect.top},{rect.right},{rect.bottom}) w={w}, h={h}")
        if w > 200 and h > 200:
            game_hwnds.append(hwnd)
    return True

cb = WNDENUMPROC(enum_windows_callback)
user32.EnumWindows(cb, 0)
print("Game HWNDs found:", game_hwnds)
