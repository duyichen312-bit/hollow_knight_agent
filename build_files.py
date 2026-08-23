import os

files = {}
files['core/perception/__init__.py'] = ''
files['core/brain/__init__.py'] = ''
files['core/controller/__init__.py'] = ''
files['core/ui/__init__.py'] = ''
files['core/__init__.py'] = ''

files['core/perception/hud_detector.py'] = '''import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class HUDState:
    health: int
    max_health: int
    soul_ratio: float
    geo: int
    is_alive: bool
    confidence: float

class HUDDetector:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.health_roi = self.config.get(" health_roi\, [0.02, 0.06, 0.16, 0.32])
 self.soul_roi = self.config.get(\soul_roi\, [0.02, 0.01, 0.18, 0.09])
 self.last_known_max_health = 5
 self.last_known_health = 5

 def detect(self, frame: np.ndarray) -> HUDState:
 h, w = frame.shape[:2]
 hy1, hx1, hy2, hx2 = [int(self.health_roi[0]*h), int(self.health_roi[1]*w),
 int(self.health_roi[2]*h), int(self.health_roi[3]*w)]
 health_crop = frame[hy1:hy2, hx1:hx2]
 health_masks, max_masks = self._count_health_masks(health_crop)
 if max_masks > 0:
 self.last_known_max_health = max(max_masks, self.last_known_max_health)
 self.last_known_health = health_masks
 else:
 health_masks = self.last_known_health
 max_masks = self.last_known_max_health

 sy1, sx1, sy2, sx2 = [int(self.soul_roi[0]*h), int(self.soul_roi[1]*w),
 int(self.soul_roi[2]*h), int(self.soul_roi[3]*w)]
 soul_crop = frame[sy1:sy2, sx1:sx2]
 soul_ratio = self._estimate_soul_ratio(soul_crop)

 return HUDState(
 health=health_masks,
 max_health=max_masks,
 soul_ratio=soul_ratio,
 geo=0,
 is_alive=(health_masks > 0),
 confidence=0.92 if max_masks > 0 else 0.5
 )

 def _count_health_masks(self, crop: np.ndarray) -> Tuple[int, int]:
 if crop.size == 0:
 return 0, 0
 gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
 _, thresh = cv2.threshold(gray, 185, 255, cv2.THRESH_BINARY)
 kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
 opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
 contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
 min_mask_area = (crop.shape[0] * crop.shape[1]) * 0.015
 max_mask_area = (crop.shape[0] * crop.shape[1]) * 0.35
 valid_masks = []
 for c in contours:
 area = cv2.contourArea(c)
 if min_mask_area < area < max_mask_area:
 x, y, w, h = cv2.boundingRect(c)
 aspect = float(w) / max(h, 1)
 if 0.5 <= aspect <= 1.8:
 valid_masks.append((x, y, w, h))
 active_masks = len(valid_masks)
 max_masks = max(active_masks, 5)
 return active_masks, max_masks

 def _estimate_soul_ratio(self, crop: np.ndarray) -> float:
 if crop.size == 0:
 return 0.0
 hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
 val = hsv[:, :, 2]
 ch, cw = val.shape
 center_mask = np.zeros((ch, cw), dtype=np.uint8)
 radius = int(min(ch, cw) * 0.38)
 cv2.circle(center_mask, (cw // 2, ch // 2), radius, 255, -1)
 mean_val = cv2.mean(val, mask=center_mask)[0]
 return float(np.clip((mean_val - 30.0) / 180.0, 0.0, 1.0))
'''

files['core/perception/knight_tracker.py'] = '''import cv2
import numpy as np
import time
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class KnightState:
 bbox: Tuple[int, int, int, int]
 center: Tuple[int, int]
 velocity: Tuple[float, float]
 facing: str
 action_state: str
 is_detected: bool

class KnightTracker:
 def __init__(self, config: dict = None):
 self.config = config or {}
 self.last_center: Optional[Tuple[int, int]] = None
 self.last_time = time.time()
 self.velocity = (0.0, 0.0)
 self.facing = \RIGHT\
 self.min_area = self.config.get(\knight_min_area\, 400)
 self.max_area = self.config.get(\knight_max_area\, 16000)

 def track(self, frame: np.ndarray) -> KnightState:
 now = time.time()
 dt = max(now - self.last_time, 0.001)
 self.last_time = now

 h, w = frame.shape[:2]
 hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

 lower_white = np.array([0, 0, 190], dtype=np.uint8)
 upper_white = np.array([180, 50, 255], dtype=np.uint8)
 mask = cv2.inRange(hsv, lower_white, upper_white)

 hud_h, hud_w = int(h * 0.22), int(w * 0.35)
 mask[0:hud_h, 0:hud_w] = 0

 kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
 mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

 contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

 best_bbox = None
 best_center = None
 min_dist_to_last = float(\inf\)

 for c in contours:
 area = cv2.contourArea(c)
 if self.min_area <= area <= self.max_area:
 x, y, cw, ch = cv2.boundingRect(c)
 aspect = float(ch) / max(cw, 1)
 if 0.6 <= aspect <= 3.0:
 cx = x + cw // 2
 cy = y + ch // 2
 if self.last_center is not None:
 dist = np.hypot(cx - self.last_center[0], cy - self.last_center[1])
 else:
 dist = np.hypot(cx - w // 2, cy - (h * 0.6))
 
 if dist < min_dist_to_last:
 min_dist_to_last = dist
 expanded_h = min(int(ch * 1.6), h - y)
 best_bbox = (x, y, cw, expanded_h)
 best_center = (cx, y + expanded_h // 2)

 if best_bbox is not None:
 cx, cy = best_center
 if self.last_center is not None:
 vx = (cx - self.last_center[0]) / dt
 vy = (cy - self.last_center[1]) / dt
 self.velocity = (0.7 * self.velocity[0] + 0.3 * vx, 0.7 * self.velocity[1] + 0.3 * vy)
 self.last_center = best_center

 if abs(self.velocity[0]) > 40:
 self.facing = \RIGHT\ if self.velocity[0] > 0 else \LEFT\

 vy = self.velocity[1]
 if abs(self.velocity[0]) > 450:
 action_state = \DASH\
 elif vy < -80:
 action_state = \AIR_JUMP\
 elif vy > 80:
 action_state = \AIR_FALL\
 else:
 action_state = \GROUND\

 return KnightState(
 bbox=best_bbox,
 center=best_center,
 velocity=self.velocity,
 facing=self.facing,
 action_state=action_state,
 is_detected=True
 )
 else:
 return KnightState(
 bbox=(0, 0, 0, 0),
 center=self.last_center or (w // 2, h // 2),
 velocity=(0.0, 0.0),
 facing=self.facing,
 action_state=\UNKNOWN\,
 is_detected=False
 )
'''

files['core/perception/enemy_detector.py'] = '''import cv2
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
 category: str

class EnemyDetector:
 def __init__(self, config: dict = None):
 self.config = config or {}
 self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
 history=20, varThreshold=30, detectShadows=False
 )

 def detect(self, frame: np.ndarray, knight_center: Tuple[int, int]) -> List[EnemyEntity]:
 h, w = frame.shape[:2]
 hud_h, hud_w = int(h * 0.22), int(w * 0.35)
 clean_frame = frame.copy()
 clean_frame[0:hud_h, 0:hud_w] = 0

 fg_mask = self.bg_subtractor.apply(clean_frame)
 hsv = cv2.cvtColor(clean_frame, cv2.COLOR_BGR2HSV)
 lower_orange = np.array([5, 120, 120], dtype=np.uint8)
 upper_orange = np.array([25, 255, 255], dtype=np.uint8)
 infection_mask = cv2.inRange(hsv, lower_orange, upper_orange)

 combined_mask = cv2.bitwise_or(fg_mask, infection_mask)
 kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
 combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
 combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

 contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 enemies: List[EnemyEntity] = []
 kx, ky = knight_center

 for c in contours:
 area = cv2.contourArea(c)
 if 300 < area < (w * h * 0.25):
 x, y, ew, eh = cv2.boundingRect(c)
 ecx = x + ew // 2
 ecy = y + eh // 2

 if abs(ecx - kx) < 30 and abs(ecy - ky) < 40:
 continue

 dist = float(np.hypot(ecx - kx, ecy - ky))
 is_airborne = (ecy < h * 0.65)
 if area > 12000:
 category = \BOSS\
 danger = 0.9
 elif is_airborne and area < 2000:
 category = \FLYER\
 danger = 0.6
 elif area < 1500:
 category = \PROJECTILE\ if is_airborne else \CRAWLER\
 danger = 0.4
 else:
 category = \CRAWLER\
 danger = 0.5

 if dist < 180:
 danger = min(1.0, danger + 0.3)

 enemies.append(EnemyEntity(
 bbox=(x, y, ew, eh),
 center=(ecx, ecy),
 distance_to_knight=dist,
 is_airborne=is_airborne,
 danger_level=danger,
 category=category
 ))

 enemies.sort(key=lambda e: e.distance_to_knight)
 return enemies[:5]
'''

files['core/perception/vision_pipeline.py'] = '''import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from core.perception.hud_detector import HUDDetector, HUDState
from core.perception.knight_tracker import KnightTracker, KnightState
from core.perception.enemy_detector import EnemyDetector, EnemyEntity

@dataclass
class FramePerception:
 hud: HUDState
 knight: KnightState
 enemies: List[EnemyEntity]
 frame_shape: tuple

class VisionPipeline:
 def __init__(self, config: dict = None):
 self.config = config or {}
 self.hud_detector = HUDDetector(self.config.get(\hud\, {}))
 self.knight_tracker = KnightTracker(self.config.get(\entity\, {}))
 self.enemy_detector = EnemyDetector(self.config.get(\entity\, {}))

 def process(self, frame: np.ndarray) -> FramePerception:
 hud_state = self.hud_detector.detect(frame)
 knight_state = self.knight_tracker.track(frame)
 enemies = self.enemy_detector.detect(frame, knight_state.center)

 return FramePerception(
 hud=hud_state,
 knight=knight_state,
 enemies=enemies,
 frame_shape=frame.shape
 )
'''

base_dir = os.path.dirname(os.path.abspath(__file__))
for rel_path, content in files.items():
 p = os.path.join(base_dir, rel_path)
 os.makedirs(os.path.dirname(p), exist_ok=True)
 with open(p, 'w', encoding='utf-8') as f:
 f.write(content)
print('All modules written successfully.')
