# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v2.0.0] - 2026-08-24 (Spatial ReAct Brain & Visual Grid Prompting Overhaul)

### 🌟 Major Architecture Milestone (智力与感知层全面重构):
1. **视觉网格增强 (Visual Prompting & 0-100 Grid Overlay)**:
   - 截屏发送给大模型前通过 OpenCV 自动叠加上 0~100 坐标标尺与半透明绿色网格（`core/perception/grid_annotator.py`）；
   - 图片分辨率自适应缩放至宽 768px（保持原始长宽比），并在 `assets/vlm_input_grid.jpg` 中实时存储带网格的输入图像供透明调试；
   - 彻底赋予多模态大模型精确的二维空间几何定位能力。
2. **短期动作与时序记忆缓冲池 (Action Context Buffer)**:
   - 新增 `ActionHistoryBuffer` 滑动窗口，记录最近 3 步决策及真实执行位移反馈（如：位移成功到达目标、撞墙卡阻停滞、受击扣血等）；
   - 每次构造 Prompt 时自动注入 3 步时序记忆，彻底根治原地打转和反复尝试无效路径的问题。
3. **ReAct 决策框架与严格 JSON 规范**:
   - 重构 System & User Prompt，强制大模型按 `态势感知(Observation) -> 避免死循环反思(Reflect) -> 空间战术决策(Action)` 进行深度推理；
   - 严格输出 JSON 结构：
     - `scene_analysis`: 角色与平台、断崖、尖刺、敌人的精确网格坐标描述；
     - `threat_level`: "LOW" / "MEDIUM" / "HIGH" / "CRITICAL"；
     - `action`: `JUMP_RIGHT_DASH`, `JUMP_CLIMB_UP`, `MOVE_RIGHT`, `SLASH_FORWARD` 等精细动作；
     - `target_coords`: `[X, Y]` 目标落脚点坐标；
     - `duration_ms`: 动作物理耗时；
     - `reasoning`: 严密空间推理链。
4. **精细动作执行器与 ReAct 战术悬浮 HUD**:
   - 本地小脑支持大跳冲刺过崖（`JUMP_RIGHT_DASH`）、多层石阶连续高跳（`JUMP_CLIMB_UP`）等精细连招；
   - 战术悬浮窗同步实时展示【态势感知】、【目标落点】、【威胁等级】、【执行动作】与【推理依据】！

---

## [v1.5.1] - 2026-08-24 (Safe Typing Suspension & Input Conflict Fix)
- 呼出文字框时安全挂起本地游戏控制，防止按键污染。

---

## [v1.5.0] - 2026-08-24 (F10 Summonable Natural Language Command Bar)
- F10 快捷召唤自然语言文字战术指令台。

---

## [v1.4.1] - 2026-08-24 (Absolute Human Directive Preemption & Fix)
- 人类指令最高优先级瞬间抢占（Level 1.5 强行熔断回溯/黑名单）。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构基线稳定版。
