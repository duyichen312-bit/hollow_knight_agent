import win32gui
import win32process

hwnds = []
def enum_cb(hwnd, extra):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    title = win32gui.GetWindowText(hwnd)
    cls = win32gui.GetClassName(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    w, h = rect[2]-rect[0], rect[3]-rect[1]
    if title or "Unity" in cls or "Hollow" in title:
        hwnds.append((hwnd, pid, title, cls, rect))

win32gui.EnumWindows(enum_cb, None)
for h in hwnds:
    if "Hollow" in h[2] or "Unity" in h[3] or h[1] == 17172:
        print(f"MATCH: HWND={h[0]}, PID={h[1]}, Title={h[2]!r}, Class={h[3]!r}, Rect={h[4]}")
