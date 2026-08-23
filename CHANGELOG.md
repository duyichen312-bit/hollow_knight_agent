# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Frozen Release)

### 🌟 Core Architectural Features:
- **双环架构 (Dual-Loop Architecture)**:
  - **战略大脑 (VLM Strategic Brain)**: 基于 Gemini 3.6 Flash，支持位置感知、全关卡拓扑解析、动态指令生成与日志持久化。
  - **战术小脑 (60Hz Reflex Cerebellum)**: 本地毫秒级微操（闪避、普攻三连击、空中下劈弹刀 Pogo、吉欧采矿）。
- **2D 银河恶魔城立体导航 (2D Spatial Metroidvania Navigation)**:
  - **死胡同两阶段脱困**: 识别不可破坏实心墙壁后，执行 6 秒纯地面长程大撤离 + 10 秒深度立体搜索。
  - **超宽禁区防折返**: 600px 范围锁定与 45 秒死墙黑名单记忆。
  - **阶梯平台优先大跳攀登**: 遇到上方石阶与悬浮平台优先高频长蓄力大跳（0.38s High Jump）。
  - **DFS 回眸侦察**: 每走两步（1.8s）极速转身 0.18s 侦察身后遗漏金币与偷袭敌人。
- **全链路日志系统 (Persistent Decision Logging)**:
  - `logs/vlm_journal.log`: 人类可读的战术演进时间轴。
  - `logs/vlm_decisions.jsonl`: 结构化数据流水，记录每一帧的模型决策与坐标。
- **纯净沉浸运行模式 (Clean Native Mode)**:
  - 一键后台启动 (`run_agent.bat`)，游戏独占前台全屏焦点，Windows 底层硬件级 DirectInput 扫描码注入。
  - 一键安全退出 (`stop_agent.bat`)。
