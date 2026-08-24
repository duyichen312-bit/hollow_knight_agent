import re
import cv2
import numpy as np
import time
from typing import Dict, Any, Optional
from core.perception.vision_pipeline import FramePerception

def clean_ascii(text: str) -> str:
    """Strips non-ascii / non-printable characters to prevent OpenCV C++ font assertion crashes."""
    if not text:
        return ""
    # Keep standard ascii and basic punctuation
    cleaned = re.sub(r"[^\x20-\x7E]", "_", str(text))
    return cleaned

class VisualDebugger:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_mono = cv2.FONT_HERSHEY_PLAIN

    def draw_hud(
        self,
        frame: np.ndarray,
        perception: FramePerception,
        fps: float,
        strategy_info: Optional[Dict[str, Any]] = None,
        active_action: Optional[str] = None
    ) -> np.ndarray:
        try:
            overlay = frame.copy()
            h, w = overlay.shape[:2]
            kx, ky = perception.knight.center

            # 1. Draw Monsters & Barriers
            for enemy in perception.enemies:
                ex, ey, ew, eh = enemy.bbox
                ecx, ecy = enemy.center
                color = (0, 80, 255) if enemy.category == "BOSS" else ((0, 160, 255) if enemy.category == "FLYER" else (0, 220, 255))
                self._draw_corner_brackets(overlay, (ex, ey, ew, eh), color, length=12, thickness=2)
                cv2.line(overlay, (kx, ky), (ecx, ecy), color, 1, cv2.LINE_AA)
                
                tag = f"{enemy.category} [{int(enemy.distance_to_knight)}px]"
                if enemy.distance_to_knight < 140 and ky < ecy:
                    tag += " [POGO READY!]"
                cv2.putText(overlay, tag, (ex, max(ey - 8, 15)), self.font, 0.45, color, 1, cv2.LINE_AA)

            # 2. Draw Geo Coins & Rocks
            for g in getattr(perception, "geo", []):
                gx, gy, gw, gh = g.bbox
                gcx, gcy = g.center
                gold_color = (0, 215, 255)
                self._draw_corner_brackets(overlay, (gx, gy, gw, gh), gold_color, length=10, thickness=2)
                cv2.line(overlay, (kx, ky), (gcx, gcy), (0, 200, 255), 1, cv2.LINE_AA)
                g_tag = "GEO ROCK" if g.is_deposit_rock else "GEO COIN"
                cv2.putText(overlay, f"{g_tag} [{int(g.distance_to_knight)}px]", (gx, max(gy - 6, 12)), self.font, 0.42, gold_color, 1, cv2.LINE_AA)

            # 3. Draw The Knight
            if perception.knight.is_detected:
                x, y, kw, kh = perception.knight.bbox
                cyan_color = (255, 255, 0)
                self._draw_corner_brackets(overlay, (x, y, kw, kh), cyan_color, length=15, thickness=2)
                
                vx, vy = perception.knight.velocity
                target_pt = (int(kx + vx * 0.2), int(ky + vy * 0.2))
                cv2.arrowedLine(overlay, (kx, ky), target_pt, (255, 200, 0), 2, cv2.LINE_AA, tipLength=0.3)
                self._draw_projected_trajectory(overlay, (kx, ky), (vx, vy), perception.knight.facing)

                k_tag = f"KNIGHT [{perception.knight.action_state} | {perception.knight.facing}]"
                cv2.putText(overlay, k_tag, (x, max(y - 8, 15)), self.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            self._draw_telemetry_panel(overlay, perception.hud, fps)
            self._draw_strategy_panel(overlay, w, strategy_info)

            if active_action:
                self._draw_action_indicator(overlay, w, h, active_action)

            return overlay
        except Exception:
            return frame

    def _draw_corner_brackets(self, img, bbox, color, length=12, thickness=2):
        x, y, w, h = bbox
        cv2.line(img, (x, y), (x + length, y), color, thickness)
        cv2.line(img, (x, y), (x, y + length), color, thickness)
        cv2.line(img, (x + w, y), (x + w - length, y), color, thickness)
        cv2.line(img, (x + w, y), (x + w, y + length), color, thickness)
        cv2.line(img, (x, y + h), (x + length, y + h), color, thickness)
        cv2.line(img, (x, y + h), (x, y + h - length), color, thickness)
        cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness)
        cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness)

    def _draw_projected_trajectory(self, img, center, velocity, facing):
        cx, cy = center
        vx, vy = velocity
        points = []
        sim_x, sim_y = float(cx), float(cy)
        sim_vx = vx if abs(vx) > 30 else (180.0 if facing == "RIGHT" else -180.0)
        sim_vy = vy - 120.0
        dt = 0.05
        gravity = 350.0

        for _ in range(12):
            points.append((int(sim_x), int(sim_y)))
            sim_x += sim_vx * dt
            sim_y += sim_vy * dt
            sim_vy += gravity * dt

        for i in range(len(points) - 1):
            alpha = max(0.2, 1.0 - (i / len(points)))
            color = (int(255 * alpha), int(220 * alpha), 0)
            cv2.line(img, points[i], points[i+1], color, 1, cv2.LINE_AA)

    def _draw_telemetry_panel(self, img, hud, fps):
        panel_w, panel_h = 320, 110
        sub = img[10:10+panel_h, 10:10+panel_w]
        if sub.shape[0] == panel_h and sub.shape[1] == panel_w:
            black_rect = np.zeros_like(sub)
            cv2.addWeighted(sub, 0.4, black_rect, 0.6, 0, sub)
            img[10:10+panel_h, 10:10+panel_w] = sub

        cv2.rectangle(img, (10, 10), (10 + panel_w, 10 + panel_h), (0, 220, 255), 1)
        cv2.putText(img, f"HOK AI HUD | {fps:.1f} FPS", (20, 32), self.font, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

        masks_str = ""
        for i in range(hud.max_health):
            masks_str += "[#] " if i < hud.health else "[ ] "
        cv2.putText(img, f"HP: {masks_str} ({hud.health}/{hud.max_health})", (20, 58), self.font, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(img, f"SOUL: {int(hud.soul_ratio * 100)}%", (20, 84), self.font, 0.45, (255, 200, 100), 1, cv2.LINE_AA)
        bar_x, bar_y, bar_w, bar_h = 105, 73, 140, 12
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (80, 80, 80), -1)
        fill_w = int(bar_w * hud.soul_ratio)
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (255, 220, 0), -1)
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 1)

        status_text = "ALIVE" if hud.is_alive else "DEAD"
        color = (0, 255, 0) if hud.is_alive else (0, 0, 255)
        cv2.putText(img, status_text, (255, 84), self.font, 0.45, color, 1, cv2.LINE_AA)

    def _draw_strategy_panel(self, img, w, strategy_info):
        panel_w, panel_h = 420, 105
        start_x = w - panel_w - 10
        sub = img[10:10+panel_h, start_x:start_x+panel_w]
        if sub.shape[0] == panel_h and sub.shape[1] == panel_w:
            black_rect = np.zeros_like(sub)
            cv2.addWeighted(sub, 0.4, black_rect, 0.6, 0, sub)
            img[10:10+panel_h, start_x:start_x+panel_w] = sub

        cv2.rectangle(img, (start_x, 10), (start_x + panel_w, 10 + panel_h), (255, 0, 200), 1)
        act = clean_ascii(strategy_info.get("action", "MOVE_RIGHT") if strategy_info else "MOVE_RIGHT")
        threat = clean_ascii(strategy_info.get("threat_level", "LOW") if strategy_info else "LOW")
        target = str(strategy_info.get("target_coords", [0, 0]) if strategy_info else [0, 0])

        cv2.putText(img, f"ACTION: {act} | THREAT: {threat}", (start_x + 12, 32), self.font, 0.50, (255, 100, 255), 1, cv2.LINE_AA)
        cv2.putText(img, f"TARGET GRID: {target}", (start_x + 12, 58), self.font, 0.45, (230, 230, 230), 1, cv2.LINE_AA)
        cv2.putText(img, f"REASON: Spatial ReAct Active", (start_x + 12, 82), self.font, 0.40, (180, 255, 180), 1, cv2.LINE_AA)

    def _draw_action_indicator(self, img, w, h, action):
        box_w, box_h = 360, 42
        bx = (w - box_w) // 2
        by = h - box_h - 20
        sub = img[by:by+box_h, bx:bx+box_w]
        if sub.shape[0] == box_h and sub.shape[1] == box_w:
            black_rect = np.zeros_like(sub)
            cv2.addWeighted(sub, 0.3, black_rect, 0.7, 0, sub)
            img[by:by+box_h, bx:bx+box_w] = sub

        clean_act = clean_ascii(action)[:32]
        cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (0, 255, 100), 2)
        cv2.putText(img, f"ACTION: {clean_act}", (bx + 10, by + 28), self.font, 0.48, (0, 255, 100), 1, cv2.LINE_AA)
