import time
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any

class FloatingOverlay:
    """
    Topmost Floating HUD Overlay (屏幕最前端无感悬浮战术HUD).
    Displays real-time VLM strategic guidance, terrain assessment, and AI/Human control status.
    Uses Win32 WS_EX_NOACTIVATE to guarantee zero focus stealing from the game.
    """
    def __init__(self, title_text: str = "Hollow Knight VLM HUD"):
        self.title_text = title_text
        self.is_running = False
        self.root: Optional[tk.Tk] = None
        self._thread: Optional[threading.Thread] = None

        # Live State Data
        self.status_text = "🤖 AI 自动运行中 (按 [F9] 暂停)"
        self.status_color = "#98c379" # Green
        self.provider_info = "Gemini 3.6 Flash"
        self.location_info = "King\'s Pass (国王山道起始区)"
        self.tactic_info = "向前探索并斩碎木门，跃下深坑进入下层"
        self.fps_info = "60.0 FPS"

    def start(self):
        self.is_running = True
        self._thread = threading.Thread(target=self._run_gui, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self.root:
            try:
                self.root.after(0, self.root.destroy)
            except Exception:
                pass

    def update_vlm_strategy(self, strategy: Dict[str, Any], provider_name: str = ""):
        if strategy:
            self.location_info = str(strategy.get("current_location", self.location_info))
            self.tactic_info = str(strategy.get("tactic", strategy.get("macro_goal", self.tactic_info)))
        if provider_name:
            self.provider_info = provider_name

    def update_control_status(self, is_paused: bool, hotkey: str = "F9", fps: float = 60.0):
        if is_paused:
            self.status_text = f"⏸️ 人类手动接管中 (按 [{hotkey}] 恢复AI)"
            self.status_color = "#e5c07b" # Amber/Yellow
        else:
            self.status_text = f"🤖 AI 自动运行中 (按 [{hotkey}] 暂停)"
            self.status_color = "#98c379" # Green
        self.fps_info = f"{fps:.1f} FPS"

    def _run_gui(self):
        self.root = tk.Tk()
        self.root.title(self.title_text)
        
        # High DPI on Windows
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Window Geometry & Always-on-Top Frameless Styling
        sw = self.root.winfo_screenwidth()
        w, h = 660, 95
        x = (sw - w) // 2
        y = 15 # Top-center positioning
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True) # Frameless
        self.root.attributes("-topmost", True) # Always on top
        self.root.attributes("-alpha", 0.90) # Semi-transparent dark glass
        self.root.configure(bg="#1e1e24")

        # Win32 Focus Protection: WS_EX_NOACTIVATE & WS_EX_TOOLWINDOW
        try:
            import win32gui
            import win32con
            hwnd = self.root.winfo_id()
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_TOPMOST
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        except Exception:
            pass

        # Main Container Frame with drag support
        container = tk.Frame(self.root, bg="#1e1e24", highlightbackground="#3e4451", highlightthickness=1)
        container.pack(fill="both", expand=True)

        # Allow dragging window
        def _start_move(event):
            self.root._x = event.x
            self.root._y = event.y

        def _on_move(event):
            deltax = event.x - self.root._x
            deltay = event.y - self.root._y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

        container.bind("<Button-1>", _start_move)
        container.bind("<B1-Motion>", _on_move)

        # 1. Top Status Row
        row1 = tk.Frame(container, bg="#1e1e24")
        row1.pack(fill="x", padx=10, pady=(6, 2))
        row1.bind("<Button-1>", _start_move)
        row1.bind("<B1-Motion>", _on_move)

        self.lbl_status = tk.Label(row1, text=self.status_text, bg="#1e1e24", fg=self.status_color, font=("Microsoft YaHei UI", 10, "bold"))
        self.lbl_status.pack(side="left")

        self.lbl_fps = tk.Label(row1, text=self.fps_info, bg="#1e1e24", fg="#abb2bf", font=("Consolas", 9))
        self.lbl_fps.pack(side="right")

        self.lbl_provider = tk.Label(row1, text=f"🧠 {self.provider_info}", bg="#1e1e24", fg="#61afef", font=("Microsoft YaHei UI", 9))
        self.lbl_provider.pack(side="right", padx=12)

        # 2. Location & Terrain Row
        row2 = tk.Frame(container, bg="#1e1e24")
        row2.pack(fill="x", padx=10, pady=(0, 2))
        row2.bind("<Button-1>", _start_move)
        row2.bind("<B1-Motion>", _on_move)

        self.lbl_location = tk.Label(row2, text=f"📍 场景: {self.location_info}", bg="#1e1e24", fg="#d19a66", font=("Microsoft YaHei UI", 9, "bold"))
        self.lbl_location.pack(side="left")

        # 3. Tactical Directive Row
        row3 = tk.Frame(container, bg="#1e1e24")
        row3.pack(fill="x", padx=10, pady=(0, 6))
        row3.bind("<Button-1>", _start_move)
        row3.bind("<B1-Motion>", _on_move)

        self.lbl_tactic = tk.Label(row3, text=f"⚔️ 战术: {self.tactic_info}", bg="#1e1e24", fg="#ffffff", font=("Microsoft YaHei UI", 9), anchor="w", wraplength=640)
        self.lbl_tactic.pack(side="left", fill="x", expand=True)

        # Refresh loop
        def _refresh():
            if not self.is_running:
                return
            try:
                self.lbl_status.config(text=self.status_text, fg=self.status_color)
                self.lbl_fps.config(text=self.fps_info)
                self.lbl_provider.config(text=f"🧠 {self.provider_info}")
                self.lbl_location.config(text=f"📍 场景: {self.location_info}")
                self.lbl_tactic.config(text=f"⚔️ 战术: {self.tactic_info}")
            except Exception:
                pass
            self.root.after(100, _refresh)

        self.root.after(100, _refresh)
        self.root.mainloop()
