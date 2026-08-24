# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.5.0] - 2026-08-24 (F10 Summonable Natural Language Command Bar)

### 🌟 New Features & Enhancements:
- **F10 快捷召唤自然语言战术文字指令台 (Command Bar)**:
  - 游戏中随时按下 **`F10`** 键（或点击悬浮窗 `💬 输入文字指令` 按钮），屏幕中央会自动呼出一个现代 Spotlight 风格的居中文字指令输入框。
  - **自然语言自由输入**:
    - 支持任意口语化战术描述，例如：
      - `"向左回溯探索搜刮金币 10秒"`
      - `"连续大跳攀登右上阶梯平台"`
      - `"向右破门推进并消灭爬虫"`
      - `"跳下深坑探秘"`
    - 按 `Enter` 提交执行，按 `Esc` 随时取消关闭。
  - **智能战术语义解析器 (`TextCommandParser`)**:
    - 本地毫秒级解析方向、时间长度（如 10s、20秒）、攀登/跳坑/破门模式，并强令本地小脑立即优先执行！
  - **自动执行与自主归还 (Auto Execution & Handover)**:
    - 指令执行期间，悬浮窗高亮显示指令内容与剩余时间；
    - 执行结束后触发提示音，**自动将控制权平滑交还给大模型自主决策**！

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
