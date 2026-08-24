# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.3.0] - 2026-08-24 (Always-on-Top Floating VLM HUD Overlay)

### 🌟 New Features & Enhancements:
- **屏幕最前端无感悬浮战术 HUD (Floating HUD Overlay)**:
  - 启动游戏后，屏幕顶部中央会自动浮现一个**暗色半透明无边框战术悬浮窗** (`core/ui/floating_overlay.py`)。
  - **实时显示**:
    1. 🟢 运行状态与热键提示（`AI 自动运行中 / 人类手动接管中 - 按 F9 切换`）；
    2. 🧠 当前调用的大模型与实时 FPS（如 `Gemini 3.6 Flash | 60.0 FPS`）；
    3. 📍 实时场景与地形定位（如 `场景: 国王山道下层洞穴区（右侧阶梯平台起点）`）；
    4. ⚔️ 大模型实时微操战术（如 `战术: 沿右上平台连续大跳攀爬，避开刺坑并消灭沿途飞虫`）。
  - **防焦点争抢与自由拖拽**:
    - 基于 Win32 `WS_EX_NOACTIVATE` 底层机制，**悬浮窗绝不抢夺游戏焦点与键盘输入**，小骑士操作丝滑流畅；
    - 支持鼠标按住悬浮窗自由拖拽到屏幕任意位置。

---

## [v1.2.0] - 2026-08-24 (Global Hotkey F9 AI Pause/Resume)
- 全局随时接管热键 `F9`：一键暂停 AI 恢复人工操作，再按一键恢复 AI。

---

## [v1.1.0] - 2026-08-24 (Model Profiles Hub & GUI Manager)
- 大模型多预设配置包与桌面端 GUI 控制中心 (`launch_model_hub.bat`)。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构（Gemini 3.6 Flash VLM 战略大脑 + 60Hz 本地战术小脑）。
