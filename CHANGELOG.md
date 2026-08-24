# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.1.0] - 2026-08-24 (Model Profiles Hub & GUI Manager)

### 🌟 New Features & Enhancements:
- **大模型多预设配置包 (Model Profiles)**:
  - 提供了预先配置好的各大主流大模型配置包：Google Gemini 官方付费版、OpenRouter (Gemini 2.5 Flash / Qwen 2.5 VL 免费版 / GPT-4o-mini / Claude 3.5 Haiku)、硅基流动 (SiliconFlow) 以及自定义/私有化本地模型 (Ollama/vLLM)。
- **桌面端可视化控制中心 (Model Hub GUI)**:
  - 新增 [`launch_model_hub.bat`](./launch_model_hub.bat) 一键启动可视化控制面板 (`model_hub_gui.py`)。
  - 支持一键下拉切换大模型配置包、在线编辑模型名称/Base URL/API Key、一键执行毫秒级连通性心跳测速，并在界面内一键启动/停止游戏 AI！
- **全格式兼容调度器 (Universal Profile Manager)**:
  - 核心大脑 `vlm_planner.py` 与 `profile_manager.py` 全面联动，模型切换实时生效且保持全量日志追踪。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构（Gemini 3.6 Flash VLM 战略大脑 + 60Hz 本地战术小脑）。
- 2D 银河恶魔城立体导航、长程死胡同脱困、DFS 节奏回眸与全量决策日志持久化。
