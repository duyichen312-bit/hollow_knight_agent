# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.2.0] - 2026-08-24 (Global Hotkey F9 AI Pause/Resume)

### 🌟 New Features & Enhancements:
- **全局接管热键 (Global Hotkey F9 Pause/Resume)**:
  - 在游戏游玩过程中，随时按下 **`F9`** 键即可**零延迟瞬间暂停 AI 控制**，系统自动释放所有按键并触发低音提示音，人类玩家可立即无缝接管操作！
  - 再次按下 **`F9`** 键，系统触发高音提示音，**AI 智能体重新无缝接管游戏控制**！
- **可视化面板联动 (Model Hub Integration)**:
  - 桌面控制中心界面增加了全局接管热键说明横幅，并在实时 HUD 状态与控制台中同步展示当前是否处于人工接管模式。
- **高响应原生监听器 (Windows Native Hotkey Listener)**:
  - 基于 Windows 底层 `GetAsyncKeyState` 实现无依赖、零卡顿全局按键捕获。

---

## [v1.1.0] - 2026-08-24 (Model Profiles Hub & GUI Manager)
- 大模型多预设配置包与桌面端 GUI 控制中心 (`launch_model_hub.bat`)。
- 一键切换、配置保存、毫秒级心跳测速与启动。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构（Gemini 3.6 Flash VLM 战略大脑 + 60Hz 本地战术小脑）。
- 2D 银河恶魔城立体导航、长程死胡同脱困、DFS 节奏回眸与全量决策日志持久化。
