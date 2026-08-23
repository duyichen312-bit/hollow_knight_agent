import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class EnemyEntity:
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    distance_to_knight: float
    is_airborne: bool
    danger_level: float
    category: str # "CRAWLER", "BARRIER", "FLYER", "BOSS"

class EnemyDetector:
    """
    Multi-signature detector for Hollow Knight:
    1. Orange Infection glow (infected bugs & bosses)
    2. Ground Crawlers / Bugs (Crawlid, TikTik)
    3. Breakable wooden gates & physical obstacles in front of the Knight
    """
    def __init__(self, config: dict = None):
        self.config = config or {}

    def detect(self, frame: np.ndarray, knight_center: Tuple[int, int]) -> List[EnemyEntity]:
        h, w = frame.shape[:2]
        kx, ky = knight_center
        enemies: List[EnemyEntity] = []

        # 1. Infection Color Detection (Orange/Amber)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_orange = np.array([8, 110, 110], dtype=np.uint8)
        upper_orange = np.array([28, 255, 255], dtype=np.uint8)
        orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
        # Mask out HUD top-left
        orange_mask[0:int(h * 0.22), 0:int(w * 0.35)] = 0

        k_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        cleaned = cv2.morphologyEx(orange_mask, cv2.MORPH_OPEN, k_kernel)
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if 120 <= area <= (w * h * 0.15):
                x, y, ew, eh = cv2.boundingRect(c)
                ecx = x + ew // 2
                ecy = y + eh // 2
                if abs(ecx - kx) < 30 and abs(ecy - ky) < 40:
                    continue
                dist = float(np.hypot(ecx - kx, ecy - ky))
                is_air = (ecy < h * 0.60)
                enemies.append(EnemyEntity(
                    bbox=(x, y, ew, eh),
                    center=(ecx, ecy),
                    distance_to_knight=dist,
                    is_airborne=is_air,
                    danger_level=0.85,
                    category="FLYER" if is_air else "CRAWLER"
                ))

        # 2. Forward Obstacle & Ground Bug Detector (ROI directly in front of the Knight)
        # In King's Pass: Crawlids on floor & wooden door barriers right in front of the Knight!
        if kx > 50 and kx < w - 250:
            front_x1 = kx + 25
            front_x2 = min(w - 10, kx + 200)
            front_y1 = max(0, ky - 50)
            front_y2 = min(h - 10, ky + 65)

            front_roi = frame[front_y1:front_y2, front_x1:front_x2]
            if front_roi.size > 0:
                gray_roi = cv2.cvtColor(front_roi, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray_roi, 50, 150)
                edge_density = float(np.count_nonzero(edges)) / max(gray_roi.size, 1)

                # High edge density in front indicates breakable wooden barrier or insect body
                if edge_density > 0.08:
                    obj_cx = (front_x1 + front_x2) // 2
                    obj_cy = (front_y1 + front_y2) // 2
                    dist = float(np.hypot(obj_cx - kx, obj_cy - ky))
                    enemies.append(EnemyEntity(
                        bbox=(front_x1, front_y1, front_x2 - front_x1, front_y2 - front_y1),
                        center=(obj_cx, obj_cy),
                        distance_to_knight=dist,
                        is_airborne=False,
                        danger_level=0.65,
                        category="BARRIER"
                    ))

        enemies.sort(key=lambda e: e.distance_to_knight)
        return enemies[:4]
