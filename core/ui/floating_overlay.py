import time
import threading
import tkinter as tk
import ctypes
from typing import Optional, Dict, Any, Callable
from core.brain.text_command_parser import TextCommandParser

user32 = ctypes.windll.user32

class FloatingOverlay:
    """
    Spatial ReAct Topmost Floating HUD Overlay with Global Stage Atlas & Sub-zone Display.
    """
    def __init__(self, title_text: str = "Hollow Knight VLM HUD", 
                 on_override_cb: Optional[Callable] = None,
                 on_typing_state_cb: Optional[Callable[[bool], None]] = None,
                 game_hwnd: Optional[int] = None):
        self.title_text = title_text
        self.on_override_cb = on_override_cb
        self.on_typing_state_cb = on_typing_state_cb
        self.game_hwnd = game_hwnd
        
        self.is_running = False
        self.is_typing_command = False
        self.root: Optional[tk.Tk] = None
        self._thread: Optional[threading.Thread] = None

        # Live State Data (Spatial ReAct & Stage Locator)
        self.status_text = "🟢 AI 空间ReAct决策中 (按 [F9] 随时接管)"
        self.status_color = "#98c379"
        self.provider_info = "Gemini 3.6 Flash"
        self.stage_info = "国王山道 (King\'s Pass) - 序章第一关"
        self.zone_info = "ZONE_A_UPPER_START (上层起始走廊)"
        self.scene_analysis_info = "小骑士位于初始区域，右侧有石阶平台与木门"
        self.action_info = "MOVE_RIGHT"
        self.target_coords_info = "[60, 60]"
        self.threat_info = "LOW"
        self.duration_info = "600ms"
        self.reasoning_info = "向前稳步探索并清理沿途障碍"
        self.fps_info = "60.0 FPS"
        self.is_override_active = False

        self._cmd_dialog: Optional[tk.Toplevel] = None

    def set_game_hwnd(self, hwnd: int):
        self.game_hwnd = hwnd

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

    def summon_text_command_box(self):
        if self.root and self.is_running:
            self.root.after(0, self._show_command_dialog)

    def _show_command_dialog(self):
        if self._cmd_dialog and self._cmd_dialog.winfo_exists():
            self._cmd_dialog.lift()
            self._cmd_dialog.focus_force()
            return

        self.is_typing_command = True
        if self.on_typing_state_cb:
            self.on_typing_state_cb(True)

        dialog = tk.Toplevel(self.root)
        dialog.title("输入战术文字指令")
        sw = dialog.winfo_screenwidth()
        sh = dialog.winfo_screenheight()
        w, h = 620, 145
        x = (sw - w) // 2
        y = (sh - h) // 3
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.overrideredirect(True)
        dialog.attributes("-topmost", True)
        dialog.configure(bg="#21252b")

        box = tk.Frame(dialog, bg="#21252b", highlightbackground="#61afef", highlightthickness=2, padx=14, pady=12)
        box.pack(fill="both", expand=True)

        lbl = tk.Label(box, text="💬 请输入战术文字指令 [此时游戏控制已暂停，请放心打字]:", bg="#21252b", fg="#e5c07b", font=("Microsoft YaHei UI", 10, "bold"))
        lbl.pack(anchor="w", pady=(0, 6))

        entry_frame = tk.Frame(box, bg="#18181f", padx=6, pady=4)
        entry_frame.pack(fill="x", pady=(0, 8))

        cmd_entry = tk.Entry(entry_frame, bg="#18181f", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Microsoft YaHei UI", 11))
        cmd_entry.pack(fill="x", expand=True)

        hint_lbl = tk.Label(box, text="💡 按 [Enter] 提交并恢复控制 | 按 [Esc] 取消 | 范例: '向左回撤并跳上悬空石台' / '连续大跳登顶'", bg="#21252b", fg="#5c6370", font=("Microsoft YaHei UI", 8))
        hint_lbl.pack(anchor="w")

        def _cleanup_and_refocus(submitted_text: Optional[str] = None):
            self.is_typing_command = False
            try:
                dialog.destroy()
            except Exception:
                pass
            self._cmd_dialog = None

            if self.on_typing_state_cb:
                self.on_typing_state_cb(False)

            if self.game_hwnd and user32.IsWindow(self.game_hwnd):
                try:
                    user32.SetForegroundWindow(self.game_hwnd)
                    user32.SwitchToThisWindow(self.game_hwnd, True)
                except Exception:
                    pass

            if submitted_text and self.on_override_cb:
                parsed = TextCommandParser.parse_command(submitted_text)
                if parsed:
                    self.on_override_cb("CUSTOM_TEXT_PLAN", parsed)

        def _on_submit(event=None):
            text = cmd_entry.get().strip()
            _cleanup_and_refocus(text if text else None)

        def _on_cancel(event=None):
            _cleanup_and_refocus(None)

        cmd_entry.bind("<Return>", _on_submit)
        cmd_entry.bind("<Escape>", _on_cancel)
        dialog.bind("<Escape>", _on_cancel)
        
        cmd_entry.delete(0, "end")
        cmd_entry.focus_force()
        self._cmd_dialog = dialog

    def update_vlm_strategy(self, strategy: Dict[str, Any], provider_name: str = "", is_human_override: bool = False):
        self.is_override_active = is_human_override
        if strategy:
            self.stage_info = str(strategy.get("current_stage", self.stage_info))
            self.zone_info = str(strategy.get("current_zone", self.zone_info))
            self.scene_analysis_info = str(strategy.get("scene_analysis", strategy.get("current_location", self.scene_analysis_info)))
            self.action_info = str(strategy.get("action", self.action_info))
            self.target_coords_info = str(strategy.get("target_coords", self.target_coords_info))
            self.threat_info = str(strategy.get("threat_level", "LOW"))
            self.duration_info = f"{strategy.get('duration_ms', 400)}ms"
            self.reasoning_info = str(strategy.get("reasoning", strategy.get("macro_goal", self.reasoning_info)))
        if provider_name:
            self.provider_info = provider_name

    def update_control_status(self, is_paused: bool, hotkey: str = "F9", fps: float = 60.0):
        if self.is_typing_command:
            self.status_text = "💬 正在输入文字指令 (本地控制已安全挂起)"
            self.status_color = "#61afef"
        elif is_paused:
            self.status_text = f"⏸️ 人类手动接管中 (按 [{hotkey}] 恢复AI)"
            self.status_color = "#e5c07b"
        elif self.is_override_active:
            self.status_text = f"🚨 人工指令优先执行中 (按 [F10] 输入新指令)"
            self.status_color = "#e06c75"
        else:
            self.status_text = f"🟢 AI 空间ReAct决策中 (按 [{hotkey}] 暂停 | [F10] 文字指令)"
            self.status_color = "#98c379"
        self.fps_info = f"{fps:.1f} FPS"

    def _trigger_override(self, action_type: str, custom_data: Optional[dict] = None):
        if self.on_override_cb:
            self.on_override_cb(action_type, custom_data)

    def _run_gui(self):
        self.root = tk.Tk()
        self.root.title(self.title_text)
        
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Window Geometry: 800x245
        sw = self.root.winfo_screenwidth()
        w, h = 800, 245
        x = (sw - w) // 2
        y = 15
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.94)
        self.root.configure(bg="#18181f")

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

        # Row 1: Header Status & Model
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

        # Row 2: Stage & Sub-zone Locator (NEW)
        row2 = tk.Frame(container, bg="#1e1e24")
        row2.pack(fill="x", padx=12, pady=(1, 2))
        row2.bind("<Button-1>", _start_move)
        row2.bind("<B1-Motion>", _on_move)

        self.lbl_stage = tk.Label(row2, text=f"🗺️ 地图: {self.stage_info}", bg="#1e1e24", fg="#61afef", font=("Microsoft YaHei UI", 9, "bold"))
        self.lbl_stage.pack(side="left")

        self.lbl_zone = tk.Label(row2, text=f"[{self.zone_info}]", bg="#1e1e24", fg="#e5c07b", font=("Microsoft YaHei UI", 9, "bold"))
        self.lbl_zone.pack(side="left", padx=8)

        # Row 3: Scene Spatial Perception
        row3 = tk.Frame(container, bg="#1e1e24")
        row3.pack(fill="x", padx=12, pady=(1, 2))
        row3.bind("<Button-1>", _start_move)
        row3.bind("<B1-Motion>", _on_move)

        self.lbl_scene = tk.Label(row3, text=f"📍 态势感知: {self.scene_analysis_info}", bg="#1e1e24", fg="#d19a66", font=("Microsoft YaHei UI", 9), anchor="w", wraplength=770)
        self.lbl_scene.pack(side="left", fill="x", expand=True)

        # Row 4: Action, Target & Threat Bar
        row4 = tk.Frame(container, bg="#1e1e24")
        row4.pack(fill="x", padx=12, pady=(1, 2))
        row4.bind("<Button-1>", _start_move)
        row4.bind("<B1-Motion>", _on_move)

        self.lbl_action = tk.Label(row4, text=f"⚔️ 决策动作: {self.action_info} [{self.duration_info}]", bg="#1e1e24", fg="#98c379", font=("Consolas", 10, "bold"))
        self.lbl_action.pack(side="left")

        self.lbl_target = tk.Label(row4, text=f"🎯 目标网格: {self.target_coords_info}", bg="#1e1e24", fg="#61afef", font=("Consolas", 10, "bold"))
        self.lbl_target.pack(side="left", padx=12)

        self.lbl_threat = tk.Label(row4, text=f"⚠️ 威胁: {self.threat_info}", bg="#1e1e24", fg="#e5c07b", font=("Consolas", 10, "bold"))
        self.lbl_threat.pack(side="left")

        # Row 5: Spatial Reasoning
        row5 = tk.Frame(container, bg="#1e1e24")
        row5.pack(fill="x", padx=12, pady=(1, 4))
        row5.bind("<Button-1>", _start_move)
        row5.bind("<B1-Motion>", _on_move)

        self.lbl_reason = tk.Label(row5, text=f"💡 推理依据: {self.reasoning_info}", bg="#1e1e24", fg="#ffffff", font=("Microsoft YaHei UI", 9), anchor="w", justify="left", wraplength=770)
        self.lbl_reason.pack(side="left", fill="x", expand=True)

        # Row 6: Quick Command Bar
        row6 = tk.Frame(container, bg="#21252b", padx=6, pady=4)
        row6.pack(fill="x", padx=8, pady=(2, 4))

        tk.Label(row6, text="⚡ 战术插队:", bg="#21252b", fg="#98c379", font=("Microsoft YaHei UI", 9, "bold")).pack(side="left", padx=(4, 6))

        btn_style = {"bg": "#3e4451", "fg": "#ffffff", "activebackground": "#61afef", "activeforeground": "#000000", "relief": "flat", "font": ("Microsoft YaHei UI", 8), "padx": 5, "pady": 1}

        tk.Button(row6, text="⬆️ 向上大跳攀登", command=lambda: self._trigger_override("CLIMB_UP"), **btn_style).pack(side="left", padx=2)
        tk.Button(row6, text="⬅️ 向左回溯探索", command=lambda: self._trigger_override("FORCE_LEFT"), **btn_style).pack(side="left", padx=2)
        tk.Button(row6, text="➡️ 向右破门推进", command=lambda: self._trigger_override("FORCE_RIGHT"), **btn_style).pack(side="left", padx=2)
        tk.Button(row6, text="⬇️ 跳下深坑探秘", command=lambda: self._trigger_override("DROP_DOWN"), **btn_style).pack(side="left", padx=2)
        
        btn_text = {"bg": "#61afef", "fg": "#1e1e24", "activebackground": "#4d97d9", "relief": "flat", "font": ("Microsoft YaHei UI", 8, "bold"), "padx": 6, "pady": 1}
        tk.Button(row6, text="💬 输入文字指令 [F10]", command=self._show_command_dialog, **btn_text).pack(side="left", padx=(6, 2))

        btn_reset = {"bg": "#e06c75", "fg": "#ffffff", "activebackground": "#c7515b", "relief": "flat", "font": ("Microsoft YaHei UI", 8, "bold"), "padx": 6, "pady": 1}
        tk.Button(row6, text="🔄 恢复大模型", command=lambda: self._trigger_override("CLEAR_OVERRIDE"), **btn_reset).pack(side="right", padx=4)

        def _refresh():
            if not self.is_running:
                return
            try:
                self.lbl_status.config(text=self.status_text, fg=self.status_color)
                self.lbl_fps.config(text=self.fps_info)
                self.lbl_provider.config(text=f"🧠 {self.provider_info}")
                self.lbl_stage.config(text=f"🗺️ 地图: {self.stage_info}")
                self.lbl_zone.config(text=f"[{self.zone_info}]")
                self.lbl_scene.config(text=f"📍 态势感知: {self.scene_analysis_info}")
                self.lbl_action.config(text=f"⚔️ 决策动作: {self.action_info} [{self.duration_info}]")
                self.lbl_target.config(text=f"🎯 目标网格: {self.target_coords_info}")
                self.lbl_threat.config(text=f"⚠️ 威胁: {self.threat_info}")
                self.lbl_reason.config(text=f"💡 推理依据: {self.reasoning_info}")
            except Exception:
                pass
            self.root.after(100, _refresh)

        self.root.after(100, _refresh)
        self.root.mainloop()
