# Hollow Knight Spatial ReAct & Demonstration AI Agent (空洞骑士空间感知与示范学习智能体)

[![GitHub Release](https://img.shields.io/badge/Release-v2.3.0-blue.svg)](https://github.com/duyichen312-bit/hollow_knight_agent/releases)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-brightgreen.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于**纯视觉输入 (DirectX / MSS 60FPS 截屏)** + **空间 ReAct 多模态大模型大脑** + **人类专家示范模仿学习 (Demonstration & Imitation Learning)** + **平台跳跃拓扑路网 (Topological Platform Graph)** 构建的《空洞骑士》自主高玩智能体。

---

## 🌟 核心能力与架构亮点

1. **🎓 人类专家示范录制与模仿学习 (v2.3.0 - Demonstration Learning)**:
   - 支持游戏中按 **`F11`** 一键挂起 AI，玩家亲自操作演示通关手法；
   - 系统自动提炼空间路标秘籍（`Waypoints Playbook`），AI 瞬间学会并自主沿专家轨迹复刻通关！
2. **🏗️ 平台跳跃拓扑路网与空间排斥探索引擎 (v2.2.0 - Topological Graph)**:
   - 将 2D 恶魔城空间抽象为平台节点与跳跃有向图，配合空间滞留热力排斥势能场，彻底根治死胡同打转！
3. **🗺️ 全关卡拓扑地图与地标定位器 (v2.1.0 - Stage Map Atlas)**:
   - 内置关卡 5 大分区地标图谱，大模型精准认知当前关卡与阶段目标。
4. **🧠 0~100 视觉网格增强与 3 步时序记忆 (v2.0.0 - Spatial ReAct)**:
   - OpenCV 半透明绿色坐标网格标尺（768px 自适应宽）+ 3 步历史时序反馈记忆池。
5. **💬 自然语言战术文字指令台 (v1.5.0 - F10 Summonable Bar)**:
   - 游戏中按 **`F10`** 呼出指令台，打字期间安全挂起游戏控制，输入自然语言战术后自动执行。
6. **⏸️ 全局热键无感人机接管 (v1.2.0 - F9 Toggle)**:
   - 随时按 **`F9`** 键瞬间释放所有按键交由人工接管，再按 **`F9`** 恢复 AI。
7. **🖥️ 置顶战术悬浮 HUD 窗 (v1.3.1 - Floating HUD)**:
   - 屏幕最前端无感悬浮展示（`WS_EX_NOACTIVATE` 零抢焦点），实时呈现态势感知、目标网格与决策推理。
8. **🎛️ 多大模型配置中心 (v1.1.0 - Model Hub)**:
   - 内置 Gemini、OpenRouter、DeepSeek、GPT-4o、Claude 3.5 Sonnet 等 7 款预设模型包与可视化切换器。

---

## 🎮 快捷键一览表

| 快捷键 | 功能描述 | 核心作用 |
| :---: | :--- | :--- |
| **`F11`** | **录制 / 结束人类示范** | 玩家亲自演示通关手法，AI 全程观摩并自动生成通关秘籍 |
| **`F10`** | **呼出文字指令台** | 输入自然语言战术指令（如“向左回撤跳上石阶”），AI 优先执行 |
| **`F9`** | **暂停 / 恢复 AI 控制** | 瞬间切换人工操作与 AI 托管 |
| **`Ctrl + 方向键`** | **战术强制插队** | 强行覆盖大模型，执行指定方向的攀爬、回溯或推进 |

---

## 🚀 快速启动指南

### 1. 克隆仓库与安装依赖
```bash
git clone https://github.com/duyichen312-bit/hollow_knight_agent.git
cd hollow_knight_agent
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）
复制 `.env.example` 为 `.env` 并填入您的 API Key：
```bash
copy .env.example .env
```

### 3. 一键启动
* **方式 1（推荐）**：双击运行 **`run_agent.bat`** 直接启动智能体；
* **方式 2（配置大模型）**：双击运行 **`launch_model_hub.bat`** 打开多模型可视化控制台选择模型包。
