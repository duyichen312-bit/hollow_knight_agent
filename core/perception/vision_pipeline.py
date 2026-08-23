import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from core.perception.hud_detector import HUDDetector, HUDState
from core.perception.knight_tracker import KnightTracker, KnightState
from core.perception.enemy_detector import EnemyDetector, EnemyEntity
from core.perception.geo_detector import GeoDetector, GeoEntity

@dataclass
class FramePerception:
    hud: HUDState
    knight: KnightState
    enemies: List[EnemyEntity]
    geo: List[GeoEntity]
    frame_shape: tuple

class VisionPipeline:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.hud_detector = HUDDetector(self.config.get("hud", {}))
        self.knight_tracker = KnightTracker(self.config.get("entity", {}))
        self.enemy_detector = EnemyDetector(self.config.get("entity", {}))
        self.geo_detector = GeoDetector(self.config.get("entity", {}))

    def process(self, frame: np.ndarray) -> FramePerception:
        hud_state = self.hud_detector.detect(frame)
        knight_state = self.knight_tracker.track(frame)
        enemies = self.enemy_detector.detect(frame, knight_state.center)
        geo_items = self.geo_detector.detect(frame, knight_state.center)

        return FramePerception(
            hud=hud_state,
            knight=knight_state,
            enemies=enemies,
            geo=geo_items,
            frame_shape=frame.shape
        )
