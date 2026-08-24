from typing import Dict, Any, Tuple

class StageMapKnowledge:
    """
    Hollow Knight Global Map Atlas & Topological Stage Locator (全关卡拓扑地图与地标定位图谱).
    Provides exact stage landmarks, coordinate sub-zones, and dead-end vs true path knowledge.
    """
    STAGE_ATLAS = {
        "KINGS_PASS": {
            "stage_name": "国王山道 (King\'s Pass) - 序章第一关",
            "global_goal": "从山道起始点出发，穿越下层洞穴，沿立体悬空石阶攀登至顶层，斩碎出口大木门抵达德特茅斯小镇",
            "zones": [
                {
                    "zone_id": "ZONE_A_UPPER_START",
                    "name": "上层起始走廊 (X: 0~100, Y: 25~45)",
                    "visual_features": "高处平整长廊、初期爬虫、右侧有封死木门与深坑断崖",
                    "true_path": "向右移动 -> 起跳挥刀劈碎木门 -> 走到右侧断崖跳下深坑进入下层",
                    "danger_notes": "木门未碎前不可直接通过，需起跳斩击2~3次破门"
                },
                {
                    "zone_id": "ZONE_B_LOWER_CENTER_SPIKES",
                    "name": "下层中央刺坑与矿石区 (X: 25~70, Y: 55~75)",
                    "visual_features": "深坑底部、地面黑色尖刺陷阱、发光吉欧矿石、悬空飞虫",
                    "true_path": "搜刮吉欧矿石爆金币 -> 向中央偏右 (X: 45~55) 寻找悬空立体石台起跳点",
                    "danger_notes": "严禁踩入地面黑色尖刺坑！"
                },
                {
                    "zone_id": "ZONE_C_LOWER_RIGHT_DEAD_END",
                    "name": "下层右侧盲端死胡同 [⚠️ 绝对陷阱死路!] (X: 72~100, Y: 58~80)",
                    "visual_features": "下层最右侧阴暗死角、封死岩壁、微弱发光粒子、右侧无任何出口",
                    "true_path": "⚠️ 警告：地面向右为绝对死路！唯一出路：立即掉头向左跑回中央 (X: 45~55)，向上大跳登上悬空平台！",
                    "danger_notes": "模型极易误判蓝光为通道！严禁在此处继续向右走！"
                },
                {
                    "zone_id": "ZONE_D_MID_AIR_CLIMB_PLATFORMS",
                    "name": "中层立体悬空阶梯区 [🔑 通关核心主干道] (X: 35~75, Y: 25~55)",
                    "visual_features": "多层悬空石阶平台、石柱悬崖、通往右上方的攀登石阶",
                    "true_path": "连续向右上方向大跳 (JUMP_CLIMB_UP) 踩上一层层悬空石台，一路攀登至高空！",
                    "danger_notes": "注意跳跃蓄力深度，避免从石台边缘滑落"
                },
                {
                    "zone_id": "ZONE_E_UPPER_EXIT_GATE",
                    "name": "顶层出口大门区 (X: 75~100, Y: 15~35)",
                    "visual_features": "最高处右侧平台、巨大出口木门、通往德特茅斯的室外强光",
                    "true_path": "起跳连续挥刀击碎出口大木门 -> 向右走出通道抵达德特茅斯小镇！",
                    "danger_notes": "击碎大门后即可通关第一关！"
                }
            ]
        }
    }

    @classmethod
    def identify_zone(cls, stage_id: str, norm_x: float, norm_y: float) -> Dict[str, Any]:
        """
        Pinpoints the exact sub-zone, topological landmark, and navigational mandate based on coordinates.
        """
        stage = cls.STAGE_ATLAS.get(stage_id, cls.STAGE_ATLAS["KINGS_PASS"])
        
        # Zone C: Lower Right Dead End
        if norm_x >= 72.0 and norm_y >= 58.0:
            return stage["zones"][2]
        
        # Zone E: Upper Exit Gate
        elif norm_x >= 75.0 and norm_y <= 38.0:
            return stage["zones"][4]

        # Zone D: Mid-air Climbing Platforms
        elif 35.0 <= norm_x <= 78.0 and 20.0 <= norm_y <= 58.0:
            return stage["zones"][3]

        # Zone A: Upper Start
        elif norm_y <= 48.0:
            return stage["zones"][0]

        # Zone B: Lower Center
        else:
            return stage["zones"][1]

    @classmethod
    def get_stage_prompt_context(cls, stage_id: str = "KINGS_PASS") -> str:
        stage = cls.STAGE_ATLAS.get(stage_id, cls.STAGE_ATLAS["KINGS_PASS"])
        lines = [
            f"【当前关卡全局拓扑地图】: {stage['stage_name']}",
            f"【通关战略目标】: {stage['global_goal']}",
            "【全地图 5 大分区地标与路线规划图】:"
        ]
        for z in stage["zones"]:
            lines.append(f"  - [{z['zone_id']}] {z['name']}")
            lines.append(f"    * 场景特征: {z['visual_features']}")
            lines.append(f"    * 正确路线: {z['true_path']}")
            lines.append(f"    * 关键警示: {z['danger_notes']}")
        return "\n".join(lines)
