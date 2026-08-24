import win32gui
import win32process
import numpy as np
import time
from typing import Optional, Tuple

try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import dxcam
    HAS_DXCAM = True
except ImportError:
    HAS_DXCAM = False

class ScreenCapture:
    """
    Multi-backend high-speed screen capture engine for Hollow Knight.
    Gracefully handles windowed, borderless, and fullscreen modes with auto-reconnect.
    """
    def __init__(self, window_title: str = "Hollow Knight"):
        self.window_title = window_title
        self.hwnd: Optional[int] = None
        self.last_frame_time = time.time()
        self.fps = 0.0
        
        self.sct = mss.mss() if HAS_MSS else None
        self.dxcam = None
        if HAS_DXCAM:
            try:
                self.dxcam = dxcam.create()
            except Exception:
                self.dxcam = None

        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        self._find_window()

    def _find_window(self) -> bool:
        self.hwnd = None
        def enum_cb(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.window_title.lower() in title.lower():
                    self.hwnd = hwnd
                    return False
        try:
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            pass

        if self.hwnd:
            print(f"[ScreenCapture] Attached to game window (HWND: {self.hwnd})")
            self._update_window_rect()
            return True
        else:
            return False

    def _update_window_rect(self):
        if self.hwnd and win32gui.IsWindow(self.hwnd):
            try:
                client_rect = win32gui.GetClientRect(self.hwnd)
                pt = win32gui.ClientToScreen(self.hwnd, (0, 0))
                left = pt[0]
                top = pt[1]
                right = left + client_rect[2]
                bottom = top + client_rect[3]
                if right > left and bottom > top:
                    self.window_rect = (left, top, right, bottom)
                else:
                    self.window_rect = win32gui.GetWindowRect(self.hwnd)
            except Exception:
                self.window_rect = None

    def capture_frame(self) -> Optional[np.ndarray]:
        now = time.time()
        dt = now - self.last_frame_time
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)
        self.last_frame_time = now

        # Method 1: DXCam (GPU Duplication)
        if self.dxcam:
            try:
                frame = self.dxcam.grab()
                if frame is not None:
                    return frame[:, :, ::-1]
            except Exception:
                pass

        # Method 2: MSS (High speed GDI)
        if self.sct:
            try:
                if self.hwnd and win32gui.IsWindow(self.hwnd):
                    self._update_window_rect()
                
                if self.window_rect:
                    l, t, r, b = self.window_rect
                    w, h = r - l, b - t
                    if w > 100 and h > 100:
                        monitor = {"left": l, "top": t, "width": w, "height": h}
                        sct_img = self.sct.grab(monitor)
                        return np.array(sct_img)[:, :, :3]

                primary = self.sct.monitors[1]
                sct_img = self.sct.grab(primary)
                return np.array(sct_img)[:, :, :3]
            except Exception:
                try:
                    self.sct = mss.mss() # Auto-reconnect stale handle
                except Exception:
                    pass

        # Method 3: PIL ImageGrab (Universal Fallback)
        if HAS_PIL:
            try:
                if self.window_rect:
                    img = ImageGrab.grab(bbox=self.window_rect)
                else:
                    img = ImageGrab.grab()
                rgb = np.array(img)
                return rgb[:, :, ::-1]
            except Exception:
                pass

        return None

    def close(self):
        if self.sct:
            try:
                self.sct.close()
            except Exception:
                pass
