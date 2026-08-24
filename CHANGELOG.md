# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v2.2.0] - 2026-08-24 (Topological Platform Graph & Frontier Navigator)

### 🌟 SOTA Architecture Implementation:
- **平台拓扑路网导航系统 (Topological Platform Graph Navigator)**:
  - 借鉴游戏 AI 与机器人 Frontier Exploration / SLAM 前沿成果，构建 `core/brain/topological_navigator.py`；
  - 彻底抛弃“平地瞎走”模式，将 2D 银河恶魔城空间抽象为**“可站立平台节点 (Platform Nodes)”**与**“跳跃/冲刺有向边 (Action Edges)”**；
  - 自动规划最短立体跳跃路线：`下层死胡同 ➔ 中央起跳点 ➔ 中层第1石台 ➔ 中层第2石台 ➔ 顶层出口`。
- **空间滞留热力与排斥势能场 (Stagnation Heatmap & Repulsion Field)**:
  - 记录每个网格的滞留时长，一旦在右下死角滞留超过 2 秒，系统产生无穷大排斥力，自动将小骑士“推”向中央石阶起跳点。
- **拓扑死胡同硬过滤器 (Dead-End Safety Filter)**:
  - 彻底拦截死胡同内的任何 `MOVE_RIGHT` 指令，强制执行 `JUMP_LEFT` 跃向中央。

---

## [v2.1.0] - 2026-08-24 (Stage Map Knowledge Atlas & Dead-End Hard Breaker)
- 全局关卡拓扑地图知识库与死胡同硬熔断。

---

## [v2.0.1] - 2026-08-24 (Self-Healing Loop & Crash Guard Hardening)
- 主循环单帧自愈保护与全量崩溃转储加固。

---

## [v2.0.0] - 2026-08-24 (Spatial ReAct Brain & Visual Grid Prompting Overhaul)
- 智力与感知层全面重构里程碑版。
