import os
import sys
import numpy as np
import cv2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.perception.vision_pipeline import VisionPipeline
from core.ui.visual_debugger import VisualDebugger

def create_mock_game_frame(w=1280, h=720) -> np.ndarray:
    # 1. Dark cavern background
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:, :] = (25, 20, 18)

    # Ground platform
    cv2.rectangle(frame, (0, int(h * 0.75)), (w, h), (45, 40, 35), -1)
    cv2.line(frame, (0, int(h * 0.75)), (w, int(h * 0.75)), (80, 75, 70), 2)

    # 2. Draw HUD (Top-Left)
    # Soul vessel orb
    cv2.circle(frame, (int(w * 0.045), int(h * 0.08)), int(h * 0.05), (200, 220, 240), -1)
    cv2.circle(frame, (int(w * 0.045), int(h * 0.08)), int(h * 0.05), (100, 100, 100), 2)
    # 5 Health Masks
    for i in range(5):
        mx = int(w * 0.10 + i * (w * 0.032))
        my = int(h * 0.08)
        cv2.ellipse(frame, (mx, my), (int(w * 0.012), int(h * 0.025)), 0, 0, 360, (235, 240, 245), -1)
        cv2.circle(frame, (mx - 4, my - 2), 2, (20, 20, 20), -1)
        cv2.circle(frame, (mx + 4, my - 2), 2, (20, 20, 20), -1)

    # 3. Draw The Knight
    kx, ky = int(w * 0.4), int(h * 0.62)
    cv2.ellipse(frame, (kx, ky), (20, 26), 0, 0, 360, (245, 245, 250), -1)
    cv2.fillPoly(frame, [np.array([[kx-18, ky-15], [kx-28, ky-45], [kx-5, ky-20]], dtype=np.int32)], (245, 245, 250))
    cv2.fillPoly(frame, [np.array([[kx+18, ky-15], [kx+28, ky-45], [kx+5, ky-20]], dtype=np.int32)], (245, 245, 250))
    cv2.ellipse(frame, (kx - 8, ky + 2), (4, 8), -15, 0, 360, (15, 15, 15), -1)
    cv2.ellipse(frame, (kx + 8, ky + 2), (4, 8), 15, 0, 360, (15, 15, 15), -1)
    cv2.fillPoly(frame, [np.array([[kx-18, ky+20], [kx+18, ky+20], [kx+22, ky+65], [kx-22, ky+65]], dtype=np.int32)], (40, 35, 45))

    # 4. Draw an Infected Enemy (Crawlid / Bug)
    ex, ey = int(w * 0.65), int(h * 0.70)
    cv2.ellipse(frame, (ex, ey), (35, 22), 0, 0, 360, (0, 140, 255), -1)
    cv2.ellipse(frame, (ex, ey), (40, 26), 0, 0, 360, (0, 100, 200), 2)
    cv2.circle(frame, (ex - 15, ey - 5), 4, (0, 220, 255), -1)

    return frame

def run_mock_test():
    print('[Test] Generating synthetic game frame...')
    frame = create_mock_game_frame()
    
    print('[Test] Initializing vision pipeline...')
    pipeline = VisionPipeline()
    debugger = VisualDebugger()

    perception = pipeline.process(frame)
    print(f'[Test] Detected Health: {perception.hud.health}/{perception.hud.max_health}')
    print(f'[Test] Detected Soul Ratio: {perception.hud.soul_ratio:.2f}')
    print(f'[Test] Detected Knight: bbox={perception.knight.bbox}, center={perception.knight.center}, state={perception.knight.action_state}')
    print(f'[Test] Detected Enemies: count={len(perception.enemies)}')

    strategy_mock = {
        'goal': 'Advance to right platform, execute Pogo on Crawlid',
        'tactic': 'Jump -> Downward Slash (Pogo) -> Reset Jump'
    }

    hud_result = debugger.draw_hud(
        frame=frame,
        perception=perception,
        fps=60.0,
        strategy_info=strategy_mock,
        active_action='POGO_SLASH'
    )

    out_path = os.path.join(BASE_DIR, 'assets', 'mock_hud_demo.png')
    cv2.imwrite(out_path, hud_result)
    print(f'[Test] Rendered demo HUD saved to: {out_path}')

if __name__ == '__main__':
    run_mock_test()
