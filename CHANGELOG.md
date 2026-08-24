# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v1.4.1] - 2026-08-24 (Absolute Human Directive Preemption & Fix)

### 🌟 Bug Fixes & Preemption Optimization:
- **彻底解决人类指令被死胡同回溯/黑名单拦截问题 (Preemption Hierarchy Fix)**:
  - 经排查日志，此前当小骑士处于死胡同 16 秒长程脱困阶段或命中 600px 黑名单禁区时，状态机优先执行了内部回溯逻辑，导致人类下发的 `Ctrl+Left` 或按钮指令被意外过滤；
  - **解决方案**: 将【人类战术指令】提升为 **最高优先判定等级（Level 1.5 最高战略抢占）**；
  - 一旦收到人类指令，状态机**瞬间熔断一切死胡同回溯、无视防折返黑名单禁区、立即清空内部停滞计数**，小脑在 10 毫秒内 100% 执行您的方向与动作！
- **全局按键采样率与按压态优化**:
  - 热键捕获全面升级为 `0x8000` 实时按压态检测，彻底杜绝丢键。

---

## [v1.4.0] - 2026-08-24 (Human Strategic Directive Override System)
- 人类战略指令强行插队系统（HUD 按钮 & 组合键插队）。

---

## [v1.3.1] - 2026-08-24 (Expanded Floating Overlay HUD)
- 悬浮窗高度翻倍扩展至 190px。

---

## [v1.0.0-stable] - 2026-08-24 (Baseline Release)
- 双环架构基线稳定版。
