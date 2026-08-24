# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v2.3.0] - 2026-08-24 (Human Demonstration & Imitation Learning System)

### 🌟 New Major Capability: 人类专家示范录制与模仿学习
- **人类专家示范实时录制器 (Demonstration Recorder)**:
  - 新增 `core/imitation/demonstration_recorder.py`；
  - 按下全局快捷键 **`F11`**（或点击悬浮窗 **`🔴 录制示范 [F11]`**），AI 瞬间挂起并进入“观摩学习模式”；
  - 玩家亲自操作游戏（跑动、跳跃、蓄力攀爬、破门、冲刺），系统以 20Hz 实时采样并提炼压缩为关键空间路标点（Waypoints）。
- **专家通关秘籍库 (Playbook Manager & Few-Shot Injection)**:
  - 新增 `core/imitation/playbook_manager.py` 与 `trajectories/expert_kings_pass.json`；
  - 录制完成后再次按下 **`F11`**，系统自动将玩家的通关轨迹固化为结构化“通关秘籍”；
  - 大模型每次决策时自动对齐玩家专家的路标动作，小脑直接沿专家示范轨迹自主复刻通关！

---

## [v2.2.0] - 2026-08-24 (Topological Platform Graph & Frontier Navigator)
- 平台跳跃拓扑路网与空间排斥探索引擎。

---

## [v2.1.0] - 2026-08-24 (Stage Map Knowledge Atlas & Dead-End Hard Breaker)
- 全局关卡拓扑地图知识库与死胡同硬熔断。

---

## [v2.0.1] - 2026-08-24 (Self-Healing Loop & Crash Guard Hardening)
- 主循环单帧自愈保护与全量崩溃转储加固。

---

## [v2.0.0] - 2026-08-24 (Spatial ReAct Brain & Visual Grid Prompting Overhaul)
- 智力与感知层全面重构里程碑版。
