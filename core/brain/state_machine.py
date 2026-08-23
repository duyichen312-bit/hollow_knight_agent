import time
from typing import Optional, Dict, Any, List, Tuple
from core.perception.vision_pipeline import FramePerception
from core.controller.gamepad import GameController

class ReflexStateMachine:
    """
    Grandmaster Depth-First Search (DFS) 2D Cerebellum AI with:
    1. Long-Distance Dead-End Escape (6.0s 纯地面长程大撤离 + 10.0s 深度立体搜索，彻底脱离死胡同)
    2. Long-Term Direction Reversal Lock (反向探索长效锁定 45 秒，严禁折返撞死墙)
    3. Wide-Radius Wall Blacklist (600px 超宽防折返禁区)
    4. Rhythmic Glance-Back Reconnaissance (走两步往回看一眼)
    5. Upward Platform Priority & Combat Reflexes
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
        # 1. EMERGENCY DAMAGE EVASION
        # =========================================================================
        if hud.health < self.last_known_health:
            self.last_known_health = hud.health
            evade_dir = "left" if knight.facing == "RIGHT" else "right"
            self.controller.dash_evade(evade_dir)
            return f"DAMAGE_EVADE_{evade_dir.upper()}"
        self.last_known_health = hud.health

        # =========================================================================
        # 2. COMBAT REFLEX: Attack Monsters & Aerial Pogo
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
        # 3. GEO GATHERING & MINING
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
        # 4. LONG-DISTANCE DEAD-END ESCAPE & SUSTAINED BACKTRACKING
        # =========================================================================
        if self.is_backtracking:
            self.is_glancing_back = False
            
            # Phase 1: Pure ground retreat run away from dead end (6.0 seconds!)
            if now < self.retreat_phase_until:
                self.controller.set_movement(self.backtrack_dir)
                remain = round(self.retreat_phase_until - now, 1)
                return f"LONG_ESCAPE_RUN_{self.backtrack_dir.upper()}[{remain}s]"
            
            # Phase 2: Upward climbing & deep branch search (10.0 seconds / Total 16.0s!)
            elif now < self.backtrack_until:
                if now - self.last_jump_time > 0.80:
                    self.controller.tap_jump(0.38) # High Jump for platform climb
                    self.last_jump_time = now
                self.controller.set_movement(self.backtrack_dir)
                remain = round(self.backtrack_until - now, 1)
                return f"DEEP_BRANCH_CLIMB_{self.backtrack_dir.upper()}[{remain}s]"
            
            # Phase Complete -> Permanently switch locked exploration direction!
            else:
                self.is_backtracking = False
                self.locked_explore_dir = self.backtrack_dir
                print(f"[AI 导航] 彻底脱离死胡同！锁定向 {self.locked_explore_dir.upper()} 方向探索新主干道！")

        # Determine macro desired direction
        nav_mode = "HORIZONTAL_EXPLORE"
        nav_dir = self.locked_explore_dir
        vert_action = "NONE"

        if strategy:
            nav_mode = strategy.get("navigation_mode", "HORIZONTAL_EXPLORE")
            s_dir = str(strategy.get("direction", "")).lower()
            if s_dir in ["left", "right"]:
                nav_dir = s_dir
            vert_action = strategy.get("vertical_action", "NONE")

        # Check wide-radius dead end blacklist (600px radius!)
        for dead_x, dead_d, _ in self.dead_end_cooldowns:
            if dead_d == nav_dir and abs(kx - dead_x) < 600:
                nav_dir = "left" if nav_dir == "right" else "right"
                self.locked_explore_dir = nav_dir
                break

        # High Sensitivity Blockage Tracking
        if abs(kx - self.last_kx) < 3 and knight.is_detected:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.slash_attempts_on_wall = 0
        self.last_kx = kx
        self.last_ky = ky

        # If blocked by obstacle:
        if self.stuck_counter > 2:
            self.is_glancing_back = False
            # 1. Test break barrier: 2 test hits
            if self.slash_attempts_on_wall < 2:
                if now - self.last_jump_time > 0.35:
                    self.controller.jump_and_slash(nav_dir, repeats=2)
                    self.last_jump_time = now
                    self.last_attack_time = now
                    self.slash_attempts_on_wall += 1
                    self.stuck_counter = 0
                    return f"TEST_BARRIER_{self.slash_attempts_on_wall}/2"
            
            # 2. Slashed 2 times, still blocked -> TRIGGER EXTENDED ESCAPE & LONG-TERM REVERSAL
            else:
                opposite_dir = "left" if nav_dir == "right" else "right"
                print(f"\n[AI 深度脱困系统] >>> 在 ({kx}, {ky}) 识别死胡同！启动 6 秒长程大撤离 + 10 秒深度立体搜索（总计 16 秒）！<<<")
                self.is_backtracking = True
                self.retreat_phase_until = now + 6.0  # 6.0s pure ground escape
                self.backtrack_until = now + 16.0     # 16.0s total deep branch search
                self.backtrack_dir = opposite_dir
                self.locked_explore_dir = opposite_dir # Lock direction to opposite
                self.dead_end_cooldowns.append((kx, nav_dir, now + 45.0)) # 600px blacklist for 45s!
                self.stuck_counter = 0
                self.slash_attempts_on_wall = 0
                
                self.controller.set_movement(opposite_dir)
                return f"TRIGGER_LONG_ESCAPE_{opposite_dir.upper()}"

        # 5. DFS RECONNAISSANCE: "走两步往回看" (Only during normal advance)
        if not self.is_backtracking and (hud.health == self.last_known_health):
            if self.is_glancing_back:
                if now < self.glance_until:
                    rear_dir = "left" if nav_dir == "right" else "right"
                    self.controller.set_movement(rear_dir)
                    return f"DFS_GLANCE_BACK_{rear_dir.upper()}"
                else:
                    self.is_glancing_back = False
                    self.last_glance_time = now
            elif now - self.last_glance_time > 2.0:
                self.is_glancing_back = True
                self.glance_until = now + 0.18
                rear_dir = "left" if nav_dir == "right" else "right"
                self.controller.set_movement(rear_dir)
                return f"DFS_CHECK_BEHIND_{rear_dir.upper()}"

        # 6. Upward Platform Priority
        if nav_mode == "UPWARD_CLIMB" or vert_action == "JUMP_CLIMB_UP":
            if now - self.last_jump_time > 0.85:
                self.climb_step += 1
                climb_dir = nav_dir if (self.climb_step % 4 != 0) else ("left" if nav_dir == "right" else "right")
                self.controller.set_movement(climb_dir)
                self.controller.tap_jump(0.38)
                self.last_jump_time = now
                return f"PRIORITY_UPWARD_JUMP_{climb_dir.upper()}"

        # Preemptive exploratory swing
        if now - self.last_attack_time > 1.4:
            self.controller.set_movement(nav_dir)
            self.controller.tap_attack(0.08)
            self.last_attack_time = now
            return f"EXPLORE_SLASH_{nav_dir.upper()}"

        # Controlled Steady Movement
        self.controller.set_movement(nav_dir)
        return f"STEADY_DFS_RUN_{nav_dir.upper()}"
