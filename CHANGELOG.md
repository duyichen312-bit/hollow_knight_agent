# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.5.1] - 2026-08-24 (Safe Typing Suspension & Input Conflict Fix)

### 🌟 Bug Fixes & Usability Improvements:
- **彻底解决呼出文字框时游戏按键污染输入框问题 (Safe Typing Suspension)**:
  - 修复了按 `F10` 呼出文字指令输入框时，本地控制器仍在循环发送按键（如 `x`, `z`, 方向键）导致输入框被游戏控制字符污染的严重 BUG；
  - **解决方案**:
    1. 按下 `F10` 呼出窗口的瞬间，系统**立即自动释放所有已按下的游戏按键 (`controller.release_all()`)**；
    2. 主循环在打字期间进入**安全挂起态（Zero Keystrokes Output）**，绝不输出任何虚拟按键；
    3. 待您按下 `Enter` 提交指令（或按 `Esc` 取消）后，窗口自动关闭，**焦点无缝切回游戏画面，并立即恢复执行全新指令**！

---

## [v1.5.0] - 2026-08-24 (F10 Summonable Natural Language Command Bar)
- F10 快捷召唤自然语言文字战术指令台（自动解析与平滑交还）。

---

## [v1.4.1] - 2026-08-24 (Absolute Human Directive Preemption & Fix)
- 人类指令最高优先级瞬间抢占（Level 1.5 强行熔断回溯/黑名单）。

---

## [v1.4.0] - 2026-08-24 (Human Strategic Directive Override System)
- 人类战略指令强行插队系统（HUD 按钮 & 组合键插队）。

---

## [v1.3.1] - 2026-08-24 (Expanded Floating Overlay HUD)
- 悬浮窗高度翻倍扩展至 190px。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构基线稳定版。
