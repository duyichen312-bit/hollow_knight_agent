# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.4.0] - 2026-08-24 (Human Strategic Directive Override System)

### 🌟 New Features & Enhancements:
- **人类战略指令强行插队/覆盖系统 (Human Strategic Override)**:
  - 当大模型判断存在偏差或卡在死角时，人类玩家可以**一键中断大模型指令**，将高优先级战术指令强行注入本地小脑，强令小脑听从您的指挥！
  - **双通道指令插队方式**:
    1. **悬浮窗一键点击**: 悬浮 HUD 底部新增 5 个战术插队按钮（`⬆️ 向上大跳攀登` / `⬅️ 向左回溯探索` / `➡️ 向右破门推进` / `⬇️ 跳下深坑探秘` / `🔄 恢复大模型自主`）；
    2. **全局快捷键组合（无需切换窗口，游戏中直接按）**:
       - `Ctrl + Up`: 强制向上大跳攀爬 15 秒；
       - `Ctrl + Left`: 强制向左回溯探索 15 秒；
       - `Ctrl + Right`: 强制向右破门推进 15 秒；
       - `Ctrl + Down`: 强制向下跳崖深坑探秘 15 秒；
       - `Ctrl + Backspace` 或 `NumPad 0`: 立即清除插队指令，恢复大模型自主决策。
  - **悬浮窗红色高亮警报**: 插队期间悬浮窗自动变为红色警示 `[🚨 人工指令优先接管中: (优先权高于大模型)]` 并显示倒计时。

---

## [v1.3.1] - 2026-08-24 (Expanded Floating Overlay HUD)
- 悬浮窗高度翻倍扩展至 190px，多行开阔排版展示。

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
