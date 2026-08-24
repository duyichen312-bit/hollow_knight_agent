import time
import threading
import tkinter as tk
from typing import Optional, Dict, Any, Callable

class FloatingOverlay:
    """
    Interactive Topmost Floating HUD Overlay with Human Directive Override Buttons.
    Allows the user to click quick buttons or use hotkeys to override LLM strategies in real-time.
    """
    def __init__(self, title_text: str = "Hollow Knight VLM HUD", on_override_cb: Optional[Callable] = None):
        self.title_text = title_text
        self.on_override_cb = on_override_cb
        self.is_running = False
        self.root: Optional[tk.Tk] = None
        self._thread: Optional[threading.Thread] = None

        # Live State Data
        self.status_text = "🟢 AI 自动运行中 (按 [F9] 随时接管)"
        self.status_color = "#98c379"
        self.provider_info = "Gemini 3.6 Flash"
        self.location_info = "King\'s Pass (国王山道起始区)"
        self.phase_info = "PHASE_1_BARRIER"
        self.nav_mode_info = "HORIZONTAL_AND_UPWARD_CLIMB"
        self.macro_goal_info = "向前探索并斩碎木门，跃下深坑进入下层"
        self.tactic_info = "贴近木门起跳连斩破门；落入深坑后搜刮金币与矿脉；沿右上平台连续大跳向上攀爬登顶！"
        self.fps_info = "60.0 FPS"
        self.is_override_active = False

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

    def update_vlm_strategy(self, strategy: Dict[str, Any], provider_name: str = "", is_human_override: bool = False):
        self.is_override_active = is_human_override
        if strategy:
            self.location_info = str(strategy.get("current_location", self.location_info))
            self.phase_info = str(strategy.get("exploration_phase", self.phase_info))
            self.nav_mode_info = str(strategy.get("navigation_mode", self.nav_mode_info))
            self.macro_goal_info = str(strategy.get("macro_goal", self.macro_goal_info))
            self.tactic_info = str(strategy.get("tactic", self.tactic_info))
        if provider_name:
            self.provider_info = provider_name

    def update_control_status(self, is_paused: bool, hotkey: str = "F9", fps: float = 60.0):
        if is_paused:
            self.status_text = f"⏸️ 人类手动接管中 (按 [{hotkey}] 恢复AI)"
            self.status_color = "#e5c07b"
        elif self.is_override_active:
            self.status_text = f"🚨 人工指令优先接管中 (优先权高于大模型)"
            self.status_color = "#e06c75" # Crimson/Red
        else:
            self.status_text = f"🟢 AI 自动运行中 (按 [{hotkey}] 暂停)"
            self.status_color = "#98c379"
        self.fps_info = f"{fps:.1f} FPS"

    def _trigger_override(self, action_type: str):
        if self.on_override_cb:
            self.on_override_cb(action_type)

    def _run_gui(self):
        self.root = tk.Tk()
        self.root.title(self.title_text)
        
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Window Geometry: 740x220 for rich interaction
        sw = self.root.winfo_screenwidth()
        w, h = 740, 220
        x = (sw - w) // 2
        y = 15
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.root.configure(bg="#18181f")

        # Win32 Focus Protection
        try:
            import win32gui
            import win32con
            hwnd = self.root.winfo_id()
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_TOPMOST
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        except Exception:
            pass

        container = tk.Frame(self.root, bg="#1e1e24", highlightbackground="#4b5263", highlightthickness=1)
        container.pack(fill="both", expand=True)

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

        # Row 1: Header Status
        row1 = tk.Frame(container, bg="#1e1e24")
        row1.pack(fill="x", padx=12, pady=(6, 2))
        row1.bind("<Button-1>", _start_move)
        row1.bind("<B1-Motion>", _on_move)

        self.lbl_status = tk.Label(row1, text=self.status_text, bg="#1e1e24", fg=self.status_color, font=("Microsoft YaHei UI", 11, "bold"))
        self.lbl_status.pack(side="left")

        self.lbl_fps = tk.Label(row1, text=self.fps_info, bg="#1e1e24", fg="#abb2bf", font=("Consolas", 10))
        self.lbl_fps.pack(side="right")

        self.lbl_provider = tk.Label(row1, text=f"🧠 {self.provider_info}", bg="#1e1e24", fg="#61afef", font=("Microsoft YaHei UI", 10, "bold"))
        self.lbl_provider.pack(side="right", padx=12)

        # Row 2: Location & Phase
        row2 = tk.Frame(container, bg="#1e1e24")
        row2.pack(fill="x", padx=12, pady=(1, 2))
        row2.bind("<Button-1>", _start_move)
        row2.bind("<B1-Motion>", _on_move)

        self.lbl_location = tk.Label(row2, text=f"📍 地形: {self.location_info}", bg="#1e1e24", fg="#d19a66", font=("Microsoft YaHei UI", 10, "bold"))
        self.lbl_location.pack(side="left")

        self.lbl_phase = tk.Label(row2, text=f"[{self.phase_info}]", bg="#1e1e24", fg="#98c379", font=("Consolas", 9))
        self.lbl_phase.pack(side="left", padx=8)

        # Row 3: Macro Goal
        row3 = tk.Frame(container, bg="#1e1e24")
        row3.pack(fill="x", padx=12, pady=(1, 2))
        row3.bind("<Button-1>", _start_move)
        row3.bind("<B1-Motion>", _on_move)

        self.lbl_goal = tk.Label(row3, text=f"🚩 目标: {self.macro_goal_info}", bg="#1e1e24", fg="#e5c07b", font=("Microsoft YaHei UI", 9, "bold"), anchor="w", wraplength=710)
        self.lbl_goal.pack(side="left", fill="x", expand=True)

        # Row 4: Tactical Directive
        row4 = tk.Frame(container, bg="#1e1e24")
        row4.pack(fill="x", padx=12, pady=(1, 4))
        row4.bind("<Button-1>", _start_move)
        row4.bind("<B1-Motion>", _on_move)

        self.lbl_tactic = tk.Label(row4, text=f"⚔️ 战术: {self.tactic_info}", bg="#1e1e24", fg="#ffffff", font=("Microsoft YaHei UI", 9), anchor="w", justify="left", wraplength=710)
        self.lbl_tactic.pack(side="left", fill="x", expand=True)

        # Row 5: Quick Human Override Control Bar (NEW: 人工指令强行插队按钮区)
        row5 = tk.Frame(container, bg="#21252b", padx=6, pady=4)
        row5.pack(fill="x", padx=8, pady=(2, 4))

        tk.Label(row5, text="⚡ 快速指派:", bg="#21252b", fg="#98c379", font=("Microsoft YaHei UI", 9, "bold")).pack(side="left", padx=(4, 6))

        btn_style = {"bg": "#3e4451", "fg": "#ffffff", "activebackground": "#61afef", "activeforeground": "#000000", "relief": "flat", "font": ("Microsoft YaHei UI", 8), "padx": 6, "pady": 1}

        tk.Button(row5, text="⬆️ 向上大跳攀登", command=lambda: self._trigger_override("CLIMB_UP"), **btn_style).pack(side="left", padx=2)
        tk.Button(row5, text="⬅️ 向左回溯探索", command=lambda: self._trigger_override("FORCE_LEFT"), **btn_style).pack(side="left", padx=2)
        tk.Button(row5, text="➡️ 向右破门推进", command=lambda: self._trigger_override("FORCE_RIGHT"), **btn_style).pack(side="left", padx=2)
        tk.Button(row5, text="⬇️ 跳下深坑探秘", command=lambda: self._trigger_override("DROP_DOWN"), **btn_style).pack(side="left", padx=2)
        
        btn_reset = {"bg": "#e06c75", "fg": "#ffffff", "activebackground": "#c7515b", "relief": "flat", "font": ("Microsoft YaHei UI", 8, "bold"), "padx": 6, "pady": 1}
        tk.Button(row5, text="🔄 恢复大模型自主", command=lambda: self._trigger_override("CLEAR_OVERRIDE"), **btn_reset).pack(side="right", padx=4)

        # Refresh loop
        def _refresh():
            if not self.is_running:
                return
            try:
                self.lbl_status.config(text=self.status_text, fg=self.status_color)
                self.lbl_fps.config(text=self.fps_info)
                self.lbl_provider.config(text=f"🧠 {self.provider_info}")
                self.lbl_location.config(text=f"📍 地形: {self.location_info}")
                self.lbl_phase.config(text=f"[{self.phase_info}]")
                self.lbl_goal.config(text=f"🚩 目标: {self.macro_goal_info}")
                self.lbl_tactic.config(text=f"⚔️ 战术: {self.tactic_info}")
            except Exception:
                pass
            self.root.after(100, _refresh)

        self.root.after(100, _refresh)
        self.root.mainloop()
