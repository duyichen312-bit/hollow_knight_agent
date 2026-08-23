import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class GeoEntity:
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    distance_to_knight: float
    is_deposit_rock: bool # True if Geo rock deposit, False if loose floating coin

class GeoDetector:
    """
    Precision detector for dropped Geo coins and Geo rock clusters.
    Enables automatic money gathering and currency accumulation.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}

    def detect(self, frame: np.ndarray, knight_center: Tuple[int, int]) -> List[GeoEntity]:
        h, w = frame.shape[:2]
        kx, ky = knight_center
        geo_items: List[GeoEntity] = []

        # Mask top-left HUD area
        clean_frame = frame.copy()
        clean_frame[0:int(h * 0.22), 0:int(w * 0.35)] = 0

        hsv = cv2.cvtColor(clean_frame, cv2.COLOR_BGR2HSV)

        # 1. Geo Amber Gold Sparkle Color (H: 14-36, S: 110-255, V: 170-255)
        lower_gold = np.array([14, 110, 170], dtype=np.uint8)
        upper_gold = np.array([36, 255, 255], dtype=np.uint8)
        gold_mask = cv2.inRange(hsv, lower_gold, upper_gold)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(gold_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if 25 <= area <= 6000:
                x, y, gw, gh = cv2.boundingRect(c)
                gcx = x + gw // 2
                gcy = y + gh // 2

                # Ignore if directly overlapping the Knight
                if abs(gcx - kx) < 25 and abs(gcy - ky) < 35:
                    continue

                dist = float(np.hypot(gcx - kx, gcy - ky))
                is_rock = (area > 350) # Large clusters are Geo deposit rocks

                geo_items.append(GeoEntity(
                    bbox=(x, y, gw, gh),
                    center=(gcx, gcy),
                    distance_to_knight=dist,
                    is_deposit_rock=is_rock
                ))

        geo_items.sort(key=lambda g: g.distance_to_knight)
        return geo_items[:3]
