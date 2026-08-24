import time
import math
from typing import Dict, Any, List, Tuple, Optional

class PlatformNode:
    def __init__(self, node_id: str, name: str, x_range: Tuple[float, float], y_range: Tuple[float, float], is_dead_end: bool = False):
        self.node_id = node_id
        self.name = name
        self.x_range = x_range
        self.y_range = y_range
        self.is_dead_end = is_dead_end
        self.center_x = (x_range[0] + x_range[1]) / 2.0
        self.center_y = (y_range[0] + y_range[1]) / 2.0
        self.edges: List[Dict[str, Any]] = [] # list of {"target": node_id, "action": str, "cost": float}

    def contains(self, x: float, y: float) -> bool:
        return (self.x_range[0] <= x <= self.x_range[1]) and (self.y_range[0] <= y <= self.y_range[1])

class TopologicalPlatformNavigator:
    """
    Topological Platform Graph & Spatial Frontier Navigator for 2D Metroidvanias.
    Replaces blind flat-ground movement with topological jump-edge pathfinding and
    spatial repulsion potential fields.
    """
    def __init__(self):
        self.nodes: Dict[str, PlatformNode] = {}
        self.stagnation_heatmap: Dict[Tuple[int, int], float] = {} # (grid_x, grid_y) -> total time
        self.last_grid = (-1, -1)
        self.last_update_time = time.time()
        self._build_kings_pass_graph()

    def _build_kings_pass_graph(self):
        # 1. Define Nodes
        n_a1 = PlatformNode("NODE_A1_START", "上层起始走廊", (0.0, 55.0), (25.0, 48.0))
        n_a2 = PlatformNode("NODE_A2_BARRIER", "上层木门断崖", (55.0, 100.0), (25.0, 48.0))
        
        n_b1 = PlatformNode("NODE_B1_PIT_DROP", "下层深坑落地点", (20.0, 45.0), (55.0, 78.0))
        n_b2 = PlatformNode("NODE_B2_CENTER_MINE", "下层中央起跳台区", (45.0, 68.0), (55.0, 78.0))
        n_c = PlatformNode("NODE_C_DEAD_END", "下层右侧绝对死胡同", (68.0, 100.0), (55.0, 78.0), is_dead_end=True)
        
        n_d1 = PlatformNode("NODE_D1_MID_AIR_1", "中层第1悬空石台", (42.0, 58.0), (45.0, 56.0))
        n_d2 = PlatformNode("NODE_D2_MID_AIR_2", "中层第2悬空石台", (58.0, 76.0), (35.0, 46.0))
        n_d3 = PlatformNode("NODE_D3_MID_AIR_3", "中层第3高位石台", (42.0, 62.0), (22.0, 36.0))
        
        n_e = PlatformNode("NODE_E_EXIT_GATE", "顶层出口大门平台", (72.0, 100.0), (15.0, 35.0))

        # 2. Add Jump / Movement Directed Edges
        n_a1.edges.append({"target": "NODE_A2_BARRIER", "action": "MOVE_RIGHT", "cost": 1.0})
        n_a2.edges.append({"target": "NODE_B1_PIT_DROP", "action": "DROP_DOWN", "cost": 1.0})
        
        n_b1.edges.append({"target": "NODE_B2_CENTER_MINE", "action": "MOVE_RIGHT", "cost": 1.0})
        n_b2.edges.append({"target": "NODE_C_DEAD_END", "action": "MOVE_RIGHT", "cost": 2.0})
        
        # Dead End Escape Edge: MUST go left back to B2!
        n_c.edges.append({"target": "NODE_B2_CENTER_MINE", "action": "RETREAT_LEFT", "cost": 0.5})
        
        # Central Launchpad -> Climb Upward onto Mid-Air Platforms!
        n_b2.edges.append({"target": "NODE_D1_MID_AIR_1", "action": "JUMP_CLIMB_UP", "cost": 1.0})
        n_d1.edges.append({"target": "NODE_D2_MID_AIR_2", "action": "JUMP_RIGHT", "cost": 1.0})
        n_d2.edges.append({"target": "NODE_D3_MID_AIR_3", "action": "JUMP_LEFT", "cost": 1.0})
        n_d3.edges.append({"target": "NODE_E_EXIT_GATE", "action": "JUMP_RIGHT_DASH", "cost": 1.0})
        
        n_e.edges.append({"target": "NODE_E_EXIT_GATE", "action": "SLASH_FORWARD", "cost": 1.0})

        for n in [n_a1, n_a2, n_b1, n_b2, n_c, n_d1, n_d2, n_d3, n_e]:
            self.nodes[n.node_id] = n

    def get_current_node(self, norm_x: float, norm_y: float) -> PlatformNode:
        # Match containment
        for n in self.nodes.values():
            if n.contains(norm_x, norm_y):
                return n
        
        # Fallback to closest center
        best_node = self.nodes["NODE_B2_CENTER_MINE"]
        min_dist = float("inf")
        for n in self.nodes.values():
            dist = math.hypot(norm_x - n.center_x, norm_y - n.center_y)
            if dist < min_dist:
                min_dist = dist
                best_node = n
        return best_node

    def update_stagnation_heatmap(self, norm_x: float, norm_y: float):
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        grid_x = int(norm_x // 10) * 10
        grid_y = int(norm_y // 10) * 10
        grid_key = (grid_x, grid_y)

        self.stagnation_heatmap[grid_key] = self.stagnation_heatmap.get(grid_key, 0.0) + dt
        self.last_grid = grid_key

    def plan_next_topological_action(self, norm_x: float, norm_y: float) -> Dict[str, Any]:
        """
        Determines the optimal next action using Topological Graph Routing & Spatial Repulsion.
        """
        self.update_stagnation_heatmap(norm_x, norm_y)
        curr_node = self.get_current_node(norm_x, norm_y)
        
        # Check Repulsion in Right Dead-End
        grid_key = (int(norm_x // 10) * 10, int(norm_y // 10) * 10)
        time_in_dead_end = self.stagnation_heatmap.get(grid_key, 0.0)

        # RULE 1: If in Dead-End Node C or stagnant on the right:
        if curr_node.node_id == "NODE_C_DEAD_END" or (norm_x >= 68.0 and norm_y >= 55.0):
            return {
                "current_node": curr_node.name,
                "target_node": "中层第1悬空石台 (NODE_D1)",
                "action": "JUMP_LEFT",
                "direction": "LEFT",
                "navigation_mode": "UPWARD_CLIMB",
                "vertical_action": "JUMP_CLIMB_UP",
                "target_coords": [50, 52],
                "duration_ms": 600,
                "reasoning": f"处于下层右侧绝对死路 [滞留{time_in_dead_end:.1f}s]！强行向左大撤退至中央起跳点，准备跃上悬空石台！"
            }

        # RULE 2: If in Central Mining/Launchpad Zone B2:
        if curr_node.node_id in ["NODE_B1_PIT_DROP", "NODE_B2_CENTER_MINE"]:
            return {
                "current_node": curr_node.name,
                "target_node": "中层第1悬空石台 (NODE_D1)",
                "action": "JUMP_CLIMB_UP",
                "direction": "RIGHT",
                "navigation_mode": "UPWARD_CLIMB",
                "vertical_action": "JUMP_CLIMB_UP",
                "target_coords": [50, 52],
                "duration_ms": 700,
                "reasoning": "到达中央起跳区，执行长蓄力向上大跳登上中层第1悬空石台！"
            }

        # RULE 3: Mid-air Climbing Series
        if curr_node.node_id == "NODE_D1_MID_AIR_1":
            return {
                "current_node": curr_node.name,
                "target_node": "中层第2悬空石台 (NODE_D2)",
                "action": "JUMP_RIGHT",
                "direction": "RIGHT",
                "navigation_mode": "UPWARD_CLIMB",
                "vertical_action": "JUMP_CLIMB_UP",
                "target_coords": [65, 40],
                "duration_ms": 500,
                "reasoning": "站稳第1石台，向右上方跳跃登上第2悬空石台！"
            }

        if curr_node.node_id == "NODE_D2_MID_AIR_2":
            return {
                "current_node": curr_node.name,
                "target_node": "中层第3高位石台 (NODE_D3)",
                "action": "JUMP_LEFT",
                "direction": "LEFT",
                "navigation_mode": "UPWARD_CLIMB",
                "vertical_action": "JUMP_CLIMB_UP",
                "target_coords": [50, 28],
                "duration_ms": 500,
                "reasoning": "站稳第2石台，向左上方高跳登上第3高位石台！"
            }

        if curr_node.node_id == "NODE_D3_MID_AIR_3":
            return {
                "current_node": curr_node.name,
                "target_node": "顶层出口大门平台 (NODE_E)",
                "action": "JUMP_RIGHT_DASH",
                "direction": "RIGHT",
                "navigation_mode": "UPWARD_CLIMB",
                "vertical_action": "JUMP_CLIMB_UP",
                "target_coords": [85, 25],
                "duration_ms": 600,
                "reasoning": "已登顶高位石台！向右大跳配合冲刺跃上顶层出口平台！"
            }

        if curr_node.node_id == "NODE_E_EXIT_GATE":
            return {
                "current_node": curr_node.name,
                "target_node": "德特茅斯小镇出口",
                "action": "SLASH_FORWARD",
                "direction": "RIGHT",
                "navigation_mode": "HORIZONTAL_EXPLORE",
                "vertical_action": "NONE",
                "target_coords": [95, 25],
                "duration_ms": 500,
                "reasoning": "抵达顶层出口！连续挥刀斩碎出口大木门，进入德特茅斯！"
            }

        # Default Forward Action
        return {
            "current_node": curr_node.name,
            "target_node": "向主干道推进",
            "action": "MOVE_RIGHT",
            "direction": "RIGHT",
            "navigation_mode": "HORIZONTAL_EXPLORE",
            "vertical_action": "NONE",
            "target_coords": [curr_node.center_x + 10, curr_node.center_y],
            "duration_ms": 500,
            "reasoning": "沿拓扑平台稳步推进"
        }
