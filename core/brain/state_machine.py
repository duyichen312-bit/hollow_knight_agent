import time
from typing import Optional, Dict, Any, List, Tuple
from core.perception.vision_pipeline import FramePerception
from core.controller.gamepad import GameController

class ReflexStateMachine:
    """
    Grandmaster Spatial ReAct 2D Cerebellum AI.
    Executes fine-grained VLM spatial ReAct actions with 60Hz local reflex protection:
    1. Level 1: Emergency Damage Evasion
    2. Level 1.5: Absolute Human Directive Preemption
    3. Level 2: Combat Reflexes & Aerial Pogo
    4. Level 3: Geo Mining & Collection
    5. Level 4: Fine-grained Spatial ReAct Action Execution (JUMP_DASH / CLIMB / DROP / SLASH)
    """
    def __init__(self, controller: GameController, config: dict = None):
        self.controller = controller
        self.config = config or {}
        
        self.last_attack_time = 0.0
        self.last_jump_time = 0.0
        self.last_dash_time = 0.0
        self.last_known_health = 5
        
        # DFS Glance-Back
        self.last_glance_time = time.time()
        self.is_glancing_back = False
        self.glance_until = 0.0
        
        # Long-Distance Dead-End & Persistent Backtracking
        self.stuck_counter = 0
        self.slash_attempts_on_wall = 0
        self.is_backtracking = False
        self.retreat_phase_until = 0.0
        self.backtrack_until = 0.0
        self.backtrack_dir = "left"
        self.locked_explore_dir = "right"
        self.dead_end_cooldowns: List[Tuple[int, str, float]] = []
        
        self.last_kx = 0
        self.last_ky = 0
        self.climb_step = 0

    def step(self, perception: FramePerception, strategy: Optional[Dict[str, Any]] = None) -> str:
        now = time.time()
        hud = perception.hud
        knight = perception.knight
        enemies = perception.enemies
        geo_items = perception.geo
        kx, ky = knight.center

        # Clean expired dead-end cooldowns
        self.dead_end_cooldowns = [w for w in self.dead_end_cooldowns if w[2] > now]

        # =========================================================================
        # LEVEL 1: EMERGENCY DAMAGE EVASION
        # =========================================================================
        if hud.health < self.last_known_health:
            self.last_known_health = hud.health
            evade_dir = "left" if knight.facing == "RIGHT" else "right"
            self.controller.dash_evade(evade_dir)
            return f"DAMAGE_EVADE_{evade_dir.upper()}"
        self.last_known_health = hud.health

        # =========================================================================
        # LEVEL 1.5: ABSOLUTE HUMAN STRATEGIC OVERRIDE (人类指令最高优先级强行抢占)
        # =========================================================================
        is_human_override = (strategy and strategy.get("exploration_phase") == "HUMAN_OVERRIDE_ACTIVE")
        if is_human_override:
            self.is_backtracking = False
            self.stuck_counter = 0
            self.is_glancing_back = False
            
            override_dir = str(strategy.get("direction", "left")).lower()
            if override_dir not in ["left", "right"]:
                override_dir = "left"
            override_mode = strategy.get("navigation_mode", "HORIZONTAL_EXPLORE")
            override_vert = strategy.get("vertical_action", "NONE")
            self.locked_explore_dir = override_dir

            self.controller.set_movement(override_dir)

            if override_mode == "UPWARD_CLIMB" or override_vert == "JUMP_CLIMB_UP":
                if now - self.last_jump_time > 0.70:
                    self.controller.tap_jump(0.38)
                    self.last_jump_time = now
                    return f"HUMAN_OVERRIDE_CLIMB_{override_dir.upper()}"

            if enemies:
                target = enemies[0]
                ex, ey = target.center
                dx = ex - kx
                dy = ey - ky
                target_dir = "right" if dx >= 0 else "left"
                if abs(dx) <= 170 and abs(dy) <= 85:
                    if now - self.last_attack_time > 0.20:
                        self.controller.combo_slashes(target_dir, count=2)
                        self.last_attack_time = now
                        return f"HUMAN_COMBAT_{target_dir.upper()}"

            if now - self.last_attack_time > 1.2:
                self.controller.set_movement(override_dir)
                self.controller.tap_attack(0.08)
                self.last_attack_time = now
                return f"HUMAN_SLASH_{override_dir.upper()}"

            return f"HUMAN_FORCE_{override_dir.upper()}"

        # =========================================================================
        # LEVEL 2: COMBAT REFLEX: Attack Monsters & Aerial Pogo
        # =========================================================================
        if enemies:
            self.is_glancing_back = False
            target = enemies[0]
            ex, ey = target.center
            dx = ex - kx
            dy = ey - ky
            target_dir = "right" if dx >= 0 else "left"

            # Aerial Pogo Downward Slash
            if knight.action_state in ["AIR_JUMP", "AIR_FALL"] and dy > 15 and abs(dx) < 140:
                if now - self.last_attack_time > 0.18:
                    self.controller.pogo_slash()
                    self.last_attack_time = now
                    return "POGO_BOUNCE"

            # Close Quarters Melee Strike
            if abs(dx) <= 170 and abs(dy) <= 85:
                if now - self.last_attack_time > 0.20:
                    self.controller.combo_slashes(target_dir, count=2)
                    self.last_attack_time = now
                    return f"SLASH_COMBO_{target_dir.upper()}"

            # Approach and attack
            if 170 < abs(dx) < 360 and abs(dy) < 110:
                self.controller.set_movement(target_dir)
                if now - self.last_attack_time > 0.45:
                    self.controller.tap_attack(0.08)
                    self.last_attack_time = now
                return f"APPROACH_MONSTER_{target_dir.upper()}"

        # =========================================================================
        # LEVEL 3: GEO GATHERING & MINING
        # =========================================================================
        if geo_items and not enemies:
            self.is_glancing_back = False
            geo_target = geo_items[0]
            gx, gy = geo_target.center
            gdx = gx - kx
            gdy = gy - ky
            geo_dir = "right" if gdx >= 0 else "left"

            if geo_target.is_deposit_rock:
                if abs(gdx) < 130 and abs(gdy) < 75:
                    if now - self.last_attack_time > 0.22:
                        self.controller.combo_slashes(geo_dir, count=3)
                        self.last_attack_time = now
                        return "MINE_GEO_ROCK"
                elif abs(gdx) < 280:
                    self.controller.set_movement(geo_dir)
                    return f"APPROACH_GEO_{geo_dir.upper()}"
            elif abs(gdx) < 240 and abs(gdy) < 80:
                self.controller.set_movement(geo_dir)
                return f"COLLECT_GEO_{geo_dir.upper()}"

        # =========================================================================
        # LEVEL 4: SPATIAL ReAct ACTION EXECUTION (空间 ReAct 精细动作执行)
        # =========================================================================
        react_action = strategy.get("action", "MOVE_RIGHT") if strategy else "MOVE_RIGHT"
        duration_sec = float(strategy.get("duration_ms", 400)) / 1000.0 if strategy else 0.40
        duration_sec = max(0.15, min(1.5, duration_sec))

        # 1. JUMP + DASH (Across wide gaps / acid pits)
        if react_action in ["JUMP_RIGHT_DASH", "JUMP_LEFT_DASH"]:
            d_dir = "right" if "RIGHT" in react_action else "left"
            self.controller.set_movement(d_dir)
            if now - self.last_jump_time > 0.70:
                self.controller.tap_jump(0.35)
                self.last_jump_time = now
                time.sleep(0.18)
                self.controller.tap_dash(0.08)
                return f"REACT_{react_action}"

        # 2. UPWARD PLATFORM CLIMB
        elif react_action == "JUMP_CLIMB_UP":
            self.controller.set_movement(self.locked_explore_dir)
            if now - self.last_jump_time > 0.75:
                self.controller.tap_jump(0.40) # High jump
                self.last_jump_time = now
                return "REACT_JUMP_CLIMB_UP"

        # 3. DIAGONAL HIGH JUMP
        elif react_action in ["JUMP_RIGHT", "JUMP_LEFT"]:
            j_dir = "right" if "RIGHT" in react_action else "left"
            self.controller.set_movement(j_dir)
            if now - self.last_jump_time > 0.70:
                self.controller.tap_jump(duration_sec)
                self.last_jump_time = now
                return f"REACT_{react_action}"

        # 4. FORWARD SLASH BREAK BARRIER
        elif react_action == "SLASH_FORWARD":
            self.controller.jump_and_slash(self.locked_explore_dir, repeats=2)
            self.last_attack_time = now
            return "REACT_SLASH_BARRIER"

        # 5. FOCUS HEAL IN SAFE CORNER
        elif react_action == "FOCUS_HEAL" and hud.health < 5 and hud.soul_ratio > 0.33:
            self.controller.focus_heal(1.5)
            return "REACT_FOCUS_HEAL"

        # 6. RETREAT / BACKTRACK
        elif react_action == "RETREAT_BACKTRACK":
            opp_dir = "left" if self.locked_explore_dir == "right" else "right"
            self.locked_explore_dir = opp_dir
            self.controller.set_movement(opp_dir)
            return f"REACT_RETREAT_{opp_dir.upper()}"

        # 7. Standard Directional Run with DFS Glance
        nav_dir = "right" if "RIGHT" in react_action else ("left" if "LEFT" in react_action else self.locked_explore_dir)
        self.locked_explore_dir = nav_dir

        # DFS Glance-Back (Once every 2.5s)
        if now - self.last_glance_time > 2.5:
            self.is_glancing_back = True
            self.glance_until = now + 0.18
            self.last_glance_time = now
            rear_dir = "left" if nav_dir == "right" else "right"
            self.controller.set_movement(rear_dir)
            return f"DFS_GLANCE_{rear_dir.upper()}"

        if self.is_glancing_back and now < self.glance_until:
            rear_dir = "left" if nav_dir == "right" else "right"
            self.controller.set_movement(rear_dir)
            return f"DFS_LOOK_{rear_dir.upper()}"
        self.is_glancing_back = False

        # Exploratory sword slash while advancing
        if now - self.last_attack_time > 1.3:
            self.controller.set_movement(nav_dir)
            self.controller.tap_attack(0.08)
            self.last_attack_time = now
            return f"REACT_EXPLORE_SLASH_{nav_dir.upper()}"

        self.controller.set_movement(nav_dir)
        return f"REACT_MOVE_{nav_dir.upper()}"
