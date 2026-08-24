# Changelog

All notable changes to the Hollow Knight AI Agent will be documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/).

---

## [v2.0.1] - 2026-08-24 (Self-Healing Loop & Crash Guard Hardening)

### 🌟 Stability & Resilience Hardening:
- **单帧异常自愈熔断机制 (Per-Frame Self-Healing Loop)**:
  - 排查发现此前主循环 `while True` 内若遇到偶发性截屏句柄重置、OpenCV 字符绘制异常或文件瞬时占用，未捕获异常会导致 Python 进程静默退出；
  - **解决方案**: 在主循环内包裹 `try...except` 自愈防护层，若单帧出现瞬时偶发异常，系统自动记录日志并自愈恢复，持续稳定运行不闪退！
- **全量崩溃转储保护 (Global Crash Dump Logger)**:
  - 新增 `logs/crash_dump.log`，任何全局异常均记录完整时间戳与调用栈追踪。
- **OpenCV 字符安全过滤 (Safe ASCII Renderer)**:
  - 在 `visual_debugger.py` 中对文本进行 ASCII 安全转义，彻底杜绝 C++ OpenCV 字体渲染底层断言错误。
- **截屏句柄自动重连 (MSS Screen Capture Auto-Reconnect)**:
  - 当游戏分辨率切换或最小化还原时，截屏模块自动重置连接句柄，保持 60FPS 稳定捕获。

---

## [v2.0.0] - 2026-08-24 (Spatial ReAct Brain & Visual Grid Prompting Overhaul)
- 智力与感知层全面重构里程碑版（0~100 网格视觉提示、3 步时序动作记忆、ReAct 框架）。
