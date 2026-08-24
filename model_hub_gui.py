import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.brain.profile_manager import ProfileManager

# High DPI Awareness on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class ModelHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hollow Knight AI - 大模型配置与控制中心 (v1.1.0)")
        self.root.geometry("780x680")
        self.root.minsize(700, 600)
        self.root.configure(bg="#1e1e24")

        self.pm = ProfileManager(BASE_DIR)
        self.profiles = self.pm.get_all_profiles()
        self.active_id = self.pm.get_active_profile_id()

        self._setup_style()
        self._build_ui()
        self._load_active_profile_into_fields()

    def _setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TFrame", background="#1e1e24")
        self.style.configure("Card.TFrame", background="#2b2b36", relief="flat")
        self.style.configure("TLabel", background="#1e1e24", foreground="#e0e0e0", font=("Microsoft YaHei UI", 10))
        self.style.configure("Card.TLabel", background="#2b2b36", foreground="#e0e0e0", font=("Microsoft YaHei UI", 10))
        self.style.configure("Title.TLabel", background="#1e1e24", foreground="#ffffff", font=("Microsoft YaHei UI", 16, "bold"))
        self.style.configure("Subtitle.TLabel", background="#1e1e24", foreground="#9a9aa8", font=("Microsoft YaHei UI", 9))
        self.style.configure("Header.TLabel", background="#2b2b36", foreground="#61afef", font=("Microsoft YaHei UI", 11, "bold"))

        self.style.configure("Primary.TButton", background="#98c379", foreground="#1e1e24", font=("Microsoft YaHei UI", 10, "bold"), borderwidth=0, padding=8)
        self.style.map("Primary.TButton", background=[("active", "#7eb35e"), ("disabled", "#444450")])

        self.style.configure("Accent.TButton", background="#61afef", foreground="#1e1e24", font=("Microsoft YaHei UI", 10, "bold"), borderwidth=0, padding=8)
        self.style.map("Accent.TButton", background=[("active", "#4d97d9")])

        self.style.configure("Danger.TButton", background="#e06c75", foreground="#1e1e24", font=("Microsoft YaHei UI", 10, "bold"), borderwidth=0, padding=8)
        self.style.map("Danger.TButton", background=[("active", "#c7515b")])

        self.style.configure("Dark.TButton", background="#3e4451", foreground="#ffffff", font=("Microsoft YaHei UI", 9), borderwidth=0, padding=6)
        self.style.map("Dark.TButton", background=[("active", "#4f5666")])

    def _build_ui(self):
        # 1. Header Title
        header_frame = ttk.Frame(self.root, padding="16 12 16 8")
        header_frame.pack(fill="x")
        
        title_lbl = ttk.Label(header_frame, text="⚔️ 《空洞骑士》大模型配置与管理中心", style="Title.TLabel")
        title_lbl.pack(anchor="w")
        sub_lbl = ttk.Label(header_frame, text="支持 Google 官方、OpenRouter、硅基流动与私有化模型无缝切换 | v1.1.0", style="Subtitle.TLabel")
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Main Content Card
        main_card = ttk.Frame(self.root, style="Card.TFrame", padding=16)
        main_card.pack(fill="both", expand=True, padx=16, pady=8)

        # Section A: Preset Model Selector
        sec_a_lbl = ttk.Label(main_card, text="📦 选择大模型预设配置包 (Model Profile)", style="Header.TLabel")
        sec_a_lbl.pack(anchor="w", pady=(0, 8))

        self.profile_var = tk.StringVar(value=self.active_id)
        profile_names = [f"{p.get('name', k)} ({k})" for k, p in self.profiles.items()]
        self.profile_keys = list(self.profiles.keys())
        
        selector_frame = ttk.Frame(main_card, style="Card.TFrame")
        selector_frame.pack(fill="x", pady=(0, 12))

        self.combo = ttk.Combobox(selector_frame, values=profile_names, state="readonly", font=("Microsoft YaHei UI", 10), width=50)
        curr_idx = self.profile_keys.index(self.active_id) if self.active_id in self.profile_keys else 0
        self.combo.current(curr_idx)
        self.combo.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.combo.bind("<<ComboboxSelected>>", self._on_profile_selected)

        apply_btn = ttk.Button(selector_frame, text="✔ 设为当前生效", style="Accent.TButton", command=self._apply_selected_profile)
        apply_btn.pack(side="right")

        # Section B: Detail Config Form
        ttk.Separator(main_card, orient="horizontal").pack(fill="x", pady=10)
        
        form_frame = ttk.Frame(main_card, style="Card.TFrame")
        form_frame.pack(fill="x", pady=4)

        # Grid form fields
        ttk.Label(form_frame, text="提供商 (Provider):", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        self.provider_entry = tk.Entry(form_frame, bg="#1e1e24", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Consolas", 10))
        self.provider_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=4)

        ttk.Label(form_frame, text="模型名称 (Model):", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.model_entry = tk.Entry(form_frame, bg="#1e1e24", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Consolas", 10))
        self.model_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=4)

        ttk.Label(form_frame, text="接口地址 (Base URL):", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.base_url_entry = tk.Entry(form_frame, bg="#1e1e24", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Consolas", 10))
        self.base_url_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=4)

        ttk.Label(form_frame, text="决策周期 (秒):", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=4)
        self.interval_entry = tk.Entry(form_frame, bg="#1e1e24", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Consolas", 10))
        self.interval_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=4)

        ttk.Label(form_frame, text="API Key 变量名:", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=4)
        self.env_var_entry = tk.Entry(form_frame, bg="#1e1e24", fg="#ffffff", insertbackground="#ffffff", relief="flat", font=("Consolas", 10))
        self.env_var_entry.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=4)

        ttk.Label(form_frame, text="API Key 密钥值:", style="Card.TLabel").grid(row=5, column=0, sticky="w", pady=4)
        key_box_frame = ttk.Frame(form_frame, style="Card.TFrame")
        key_box_frame.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=4)
        
        self.api_key_entry = tk.Entry(key_box_frame, bg="#1e1e24", fg="#98c379", insertbackground="#ffffff", relief="flat", show="*", font=("Consolas", 10))
        self.api_key_entry.pack(side="left", fill="x", expand=True)

        self.show_key_btn = ttk.Button(key_box_frame, text="👁", width=3, style="Dark.TButton", command=self._toggle_key_visibility)
        self.show_key_btn.pack(side="right", padx=(6, 0))

        form_frame.columnconfigure(1, weight=1)

        # Description text
        self.desc_lbl = ttk.Label(main_card, text="", style="Card.TLabel", wraplength=700, foreground="#abb2bf")
        self.desc_lbl.pack(anchor="w", pady=(8, 4))

        # Save changes button
        save_prof_btn = ttk.Button(main_card, text="💾 保存并更新此配置包", style="Dark.TButton", command=self._save_current_profile_changes)
        save_prof_btn.pack(anchor="e", pady=(4, 8))

        # Section C: Diagnostic Ping Status Box
        ttk.Separator(main_card, orient="horizontal").pack(fill="x", pady=8)
        
        ping_header = ttk.Frame(main_card, style="Card.TFrame")
        ping_header.pack(fill="x", pady=(2, 4))
        ttk.Label(ping_header, text="📡 连通性测试与响应诊断", style="Header.TLabel").pack(side="left")
        
        self.test_btn = ttk.Button(ping_header, text="⚡ 测试当前配置连通性", style="Accent.TButton", command=self._test_connection)
        self.test_btn.pack(side="right")

        self.log_text = tk.Text(main_card, height=4, bg="#18181f", fg="#98c379", insertbackground="#ffffff", relief="flat", font=("Consolas", 9), padx=8, pady=8)
        self.log_text.pack(fill="x", pady=(4, 0))
        self.log_text.insert("end", "点击上方「测试当前配置连通性」可即时检测网络与模型可用性。\n")
        self.log_text.config(state="disabled")

        # 3. Bottom Action Bar
        bottom_bar = ttk.Frame(self.root, padding=16)
        bottom_bar.pack(fill="x")

        launch_btn = ttk.Button(bottom_bar, text="🚀 启动《空洞骑士》AI Agent", style="Primary.TButton", command=self._launch_game_agent)
        launch_btn.pack(side="left", padx=(0, 12))

        stop_btn = ttk.Button(bottom_bar, text="🛑 停止 AI 进程", style="Danger.TButton", command=self._stop_game_agent)
        stop_btn.pack(side="left")

        open_logs_btn = ttk.Button(bottom_bar, text="📂 打开日志目录", style="Dark.TButton", command=self._open_logs_folder)
        open_logs_btn.pack(side="right")

    def _on_profile_selected(self, event=None):
        idx = self.combo.current()
        if 0 <= idx < len(self.profile_keys):
            pid = self.profile_keys[idx]
            self._fill_form_with_profile(pid)

    def _load_active_profile_into_fields(self):
        self._fill_form_with_profile(self.active_id)

    def _fill_form_with_profile(self, pid: str):
        prof = self.profiles.get(pid, {})
        self.provider_entry.delete(0, "end")
        self.provider_entry.insert(0, prof.get("provider", ""))

        self.model_entry.delete(0, "end")
        self.model_entry.insert(0, prof.get("model", ""))

        self.base_url_entry.delete(0, "end")
        self.base_url_entry.insert(0, prof.get("base_url", ""))

        self.interval_entry.delete(0, "end")
        self.interval_entry.insert(0, str(prof.get("decision_interval_sec", 2.0)))

        env_var = prof.get("api_key_env", "")
        self.env_var_entry.delete(0, "end")
        self.env_var_entry.insert(0, env_var)

        key_val = self.pm.get_api_key_for_env(env_var)
        self.api_key_entry.delete(0, "end")
        self.api_key_entry.insert(0, key_val)

        desc = prof.get("description", "")
        self.desc_lbl.config(text=f"💡 说明: {desc}")

    def _toggle_key_visibility(self):
        if self.api_key_entry.cget("show") == "*":
            self.api_key_entry.config(show="")
            self.show_key_btn.config(text="🔒")
        else:
            self.api_key_entry.config(show="*")
            self.show_key_btn.config(text="👁")

    def _apply_selected_profile(self):
        idx = self.combo.current()
        if 0 <= idx < len(self.profile_keys):
            pid = self.profile_keys[idx]
            self.pm.set_active_profile(pid)
            self.active_id = pid
            messagebox.showinfo("成功", f"已成功切换当前生效大模型配置为: \n\n{self.profiles[pid].get('name')}")
            self._log_msg(f"[*] 当前生效配置已切换为: {pid}")

    def _save_current_profile_changes(self):
        idx = self.combo.current()
        if 0 <= idx < len(self.profile_keys):
            pid = self.profile_keys[idx]
            prof = self.profiles[pid]
            
            prof["provider"] = self.provider_entry.get().strip()
            prof["model"] = self.model_entry.get().strip()
            prof["base_url"] = self.base_url_entry.get().strip()
            try:
                prof["decision_interval_sec"] = float(self.interval_entry.get().strip())
            except Exception:
                prof["decision_interval_sec"] = 2.0
            
            env_var = self.env_var_entry.get().strip()
            prof["api_key_env"] = env_var
            
            key_val = self.api_key_entry.get().strip()
            self.pm.save_profile_custom(prof, key_val)
            
            messagebox.showinfo("成功", f"配置包 '{prof.get('name')}' 及对应 API Key 已成功保存！")
            self._log_msg(f"[+] 配置包 '{pid}' 保存成功！")

    def _test_connection(self):
        self.test_btn.config(state="disabled", text="⏳ 正在检测连接...")
        self._log_msg("[*] 正在向模型服务发起多模态心跳探测...")

        def _worker():
            idx = self.combo.current()
            pid = self.profile_keys[idx] if 0 <= idx < len(self.profile_keys) else self.active_id
            
            # Save any unsaved inputs temporarily for test
            key_val = self.api_key_entry.get().strip()
            env_var = self.env_var_entry.get().strip()
            if key_val:
                self.pm.set_api_key_for_env(env_var, key_val)

            success, msg, latency = self.pm.test_profile_connection(pid)
            
            self.root.after(0, lambda: self._on_test_done(success, msg))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_test_done(self, success: bool, msg: str):
        self.test_btn.config(state="normal", text="⚡ 测试当前配置连通性")
        self._log_msg(msg)

    def _log_msg(self, text: str):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", text + "\n")
        self.log_text.config(state="disabled")

    def _launch_game_agent(self):
        self._apply_selected_profile()
        bat_path = os.path.join(BASE_DIR, "run_agent.bat")
        if os.path.exists(bat_path):
            os.system(f'start "" "{bat_path}"')
            self._log_msg("[🚀] Hollow Knight AI Agent 已在后台静默启动！")

    def _stop_game_agent(self):
        bat_path = os.path.join(BASE_DIR, "stop_agent.bat")
        if os.path.exists(bat_path):
            os.system(f'start "" "{bat_path}"')
            self._log_msg("[🛑] 已发送停止信号。")

    def _open_logs_folder(self):
        logs_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        os.system(f'explorer "{logs_dir}"')

def main():
    root = tk.Tk()
    app = ModelHubApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
