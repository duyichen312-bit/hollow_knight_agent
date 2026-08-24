# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v2.1.0] - 2026-08-24 (Stage Map Knowledge Atlas & Dead-End Hard Breaker)

### 🌟 New Features & Enhancements:
- **全局关卡拓扑地图知识库 (Stage Map Knowledge Atlas)**:
  - 针对大模型在黑暗场景误把岩壁蓝光当通道导致卡在右侧死路的问题，新增 `core/brain/stage_map_knowledge.py`；
  - 完整编排了《国王山道》5 大分区的地标特征、通关真路径与陷阱死路；
  - 每次调用大模型时自动注入【全局拓扑地图】与【小骑士当前精准地标与区域定位】。
- **下层右侧死胡同硬熔断机制 (Zone C Dead-End Hard Breaker)**:
  - 在底层状态机加入地标硬保护：当检测到小骑士处于 `(X>=70, Y>=55)`（即下层右侧盲端死胡同区）时，**瞬间触发硬熔断，强行向左大撤退至中央区域并起跳攀爬悬空立体石台**，从物理层彻底杜绝卡在右侧！
- **悬浮窗全拓扑展示 (Global Stage HUD)**:
  - 战术悬浮窗新增 `🗺️ 地图: 国王山道·第1关 [ZONE_C_LOWER_RIGHT]` 实时分区定位栏。

---

## [v2.0.1] - 2026-08-24 (Self-Healing Loop & Crash Guard Hardening)
- 主循环单帧自愈保护与全量崩溃转储加固。

---

## [v2.0.0] - 2026-08-24 (Spatial ReAct Brain & Visual Grid Prompting Overhaul)
- 智力与感知层全面重构里程碑版（0~100 网格视觉提示、3 步时序动作记忆、ReAct 框架）。
