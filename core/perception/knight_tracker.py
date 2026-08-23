import cv2
import numpy as np
import time
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class KnightState:
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    velocity: Tuple[float, float]
    facing: str                     # "RIGHT" or "LEFT"
    action_state: str               # "GROUND", "AIR_JUMP", "AIR_FALL", "DASH"
    is_detected: bool

class KnightTracker:
    """
    Stable tracking of The Knight using bright white horns/mask signature.
    Includes exponential moving average smoothing to eliminate jitter.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.smooth_center: Optional[Tuple[float, float]] = None
        self.last_center: Optional[Tuple[int, int]] = None
        self.last_time = time.time()
        self.velocity = (0.0, 0.0)
        self.facing = "RIGHT"
        self.min_area = self.config.get("knight_min_area", 250)
        self.max_area = self.config.get("knight_max_area", 16000)

    def track(self, frame: np.ndarray) -> KnightState:
        now = time.time()
        dt = max(now - self.last_time, 0.001)
        self.last_time = now

        h, w = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 1. White Head/Mask HSV Range (S < 45, V > 195)
        lower_white = np.array([0, 0, 195], dtype=np.uint8)
        upper_white = np.array([180, 45, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Mask out HUD top-left
        mask[0:int(h * 0.22), 0:int(w * 0.35)] = 0

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_bbox = None
        raw_center = None
        min_dist_to_last = float("inf")

        for c in contours:
            area = cv2.contourArea(c)
            if self.min_area <= area <= self.max_area:
                x, y, cw, ch = cv2.boundingRect(c)
                aspect = float(ch) / max(cw, 1)
                
                # Knight's head & body shape
                if 0.5 <= aspect <= 3.2:
                    cx = x + cw // 2
                    cy = y + ch // 2
                    
                    if self.smooth_center is not None:
                        dist = np.hypot(cx - self.smooth_center[0], cy - self.smooth_center[1])
                    else:
                        dist = np.hypot(cx - w // 2, cy - (h * 0.65))
                    
                    if dist < min_dist_to_last and dist < 350:
                        min_dist_to_last = dist
                        expanded_h = min(int(ch * 1.5), h - y)
                        best_bbox = (x, y, cw, expanded_h)
                        raw_center = (cx, y + expanded_h // 2)

        if best_bbox is not None and raw_center is not None:
            # Exponential smoothing
            if self.smooth_center is None:
                self.smooth_center = (float(raw_center[0]), float(raw_center[1]))
            else:
                alpha = 0.65
                self.smooth_center = (
                    alpha * float(raw_center[0]) + (1.0 - alpha) * self.smooth_center[0],
                    alpha * float(raw_center[1]) + (1.0 - alpha) * self.smooth_center[1]
                )

            cx = int(self.smooth_center[0])
            cy = int(self.smooth_center[1])

            if self.last_center is not None:
                vx = (cx - self.last_center[0]) / dt
                vy = (cy - self.last_center[1]) / dt
                self.velocity = (
                    0.6 * self.velocity[0] + 0.4 * vx,
                    0.6 * self.velocity[1] + 0.4 * vy
                )
            self.last_center = (cx, cy)

            if self.velocity[0] > 30:
                self.facing = "RIGHT"
            elif self.velocity[0] < -30:
                self.facing = "LEFT"

            vy = self.velocity[1]
            if abs(self.velocity[0]) > 400:
                action_state = "DASH"
            elif vy < -70:
                action_state = "AIR_JUMP"
            elif vy > 70:
                action_state = "AIR_FALL"
            else:
                action_state = "GROUND"

            return KnightState(
                bbox=best_bbox,
                center=(cx, cy),
                velocity=self.velocity,
                facing=self.facing,
                action_state=action_state,
                is_detected=True
            )
        else:
            return KnightState(
                bbox=(0, 0, 0, 0),
                center=(int(self.smooth_center[0]) if self.smooth_center else w // 2,
                        int(self.smooth_center[1]) if self.smooth_center else int(h * 0.65)),
                velocity=(0.0, 0.0),
                facing=self.facing,
                action_state="GROUND",
                is_detected=False
            )
