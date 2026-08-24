# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.3.1] - 2026-08-24 (Expanded Floating Overlay HUD)

### 🌟 New Features & Enhancements:
- **悬浮窗高度翻倍扩展 (Doubled Height Floating HUD)**:
  - 悬浮窗垂直高度从 95px **翻倍扩展至 190px**（宽度 720px），整体排版更加开阔舒适。
  - **丰富多行战术展示**:
    - 第 1 行: 状态指示灯（🟢 AI运行中 / ⏸️ 人工接管）+ 调用模型 + 实时 FPS。
    - 第 2 行: 📍 精确地形定位 + 当前关卡阶段标签（如 `[PHASE_3_LOWER_CAVERN]`）。
    - 第 3 行: 🚩 大模型宏观战略目标。
    - 第 4 行: ⚔️ 大模型微操多行战术指引（宽幅自适应换行）。
    - 第 5 行: 💡 自由拖拽与 F9 快捷键提示条。

---

## [v1.3.0] - 2026-08-24 (Always-on-Top Floating VLM HUD Overlay)
- 屏幕最前端无感战术悬浮 HUD（基于 Win32 `WS_EX_NOACTIVATE` 零抢焦点）。

---

## [v1.2.0] - 2026-08-24 (Global Hotkey F9 AI Pause/Resume)
- 全局随时接管热键 `F9`：一键暂停 AI 恢复人工操作，再按一键恢复 AI。

---

## [v1.1.0] - 2026-08-24 (Model Profiles Hub & GUI Manager)
- 大模型多预设配置包与桌面端 GUI 控制中心 (`launch_model_hub.bat`)。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构（Gemini 3.6 Flash VLM 战略大脑 + 60Hz 本地战术小脑）。
