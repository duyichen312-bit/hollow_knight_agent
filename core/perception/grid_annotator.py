import cv2
import numpy as np
from typing import Tuple, Optional

class VisualGridAnnotator:
    """
    Visual Prompting & Coordinate Grid Annotator for Multimodal LLM Spatial Perception.
    Draws a semi-transparent 0-100 green grid with axis rulers and scale markings.
    """
    @staticmethod
    def annotate(frame: np.ndarray, target_width: int = 768, knight_norm_pos: Optional[Tuple[float, float]] = None) -> np.ndarray:
        if frame is None or frame.size == 0:
            return frame

        # 1. Resize while maintaining aspect ratio
        h_orig, w_orig = frame.shape[:2]
        target_height = int(h_orig * (target_width / w_orig))
        resized = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

        # 2. Create grid overlay plane
        overlay = resized.copy()
        grid_color = (0, 230, 100) # Bright green
        axis_color = (0, 255, 180) # Cyan-green
        text_color = (0, 255, 120)
        bg_bar_color = (15, 20, 25)

        h, w = target_height, target_width

        # Top and Left Axis Ruler Bars
        cv2.rectangle(overlay, (0, 0), (w, 18), bg_bar_color, -1)
        cv2.rectangle(overlay, (0, 0), (22, h), bg_bar_color, -1)

        # 3. Draw 10x10 Grid Lines (10% increments: 0, 10, 20, ... 100)
        for i in range(0, 101, 10):
            # Vertical lines (X-axis)
            x = int(w * (i / 100.0))
            if i > 0 and i < 100:
                cv2.line(overlay, (x, 18), (x, h), grid_color, 1, lineType=cv2.LINE_AA)
            # Tick mark and label on top ruler
            cv2.line(overlay, (x, 0), (x, 18), axis_color, 1, lineType=cv2.LINE_AA)
            if i % 20 == 0:
                cv2.putText(overlay, str(i), (max(x - 8, 2), 14), cv2.FONT_HERSHEY_SIMPLEX, 0.38, text_color, 1, lineType=cv2.LINE_AA)

            # Horizontal lines (Y-axis)
            y = int(h * (i / 100.0))
            if i > 0 and i < 100:
                cv2.line(overlay, (22, y), (w, y), grid_color, 1, lineType=cv2.LINE_AA)
            # Tick mark and label on left ruler
            cv2.line(overlay, (0, y), (22, y), axis_color, 1, lineType=cv2.LINE_AA)
            if i % 20 == 0:
                cv2.putText(overlay, str(i), (2, min(y + 4, h - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, text_color, 1, lineType=cv2.LINE_AA)

        # 4. Small intersection crosshairs
        for ix in range(20, 90, 20):
            for iy in range(20, 90, 20):
                cx = int(w * (ix / 100.0))
                cy = int(h * (iy / 100.0))
                cv2.drawMarker(overlay, (cx, cy), (0, 255, 150), markerType=cv2.MARKER_CROSS, markerSize=6, thickness=1)

        # 5. Optional Knight Marker
        if knight_norm_pos is not None:
            kx_norm, ky_norm = knight_norm_pos
            kx_px = int(w * (kx_norm / 100.0))
            ky_px = int(h * (ky_norm / 100.0))
            cv2.circle(overlay, (kx_px, ky_px), 8, (0, 255, 255), 2, lineType=cv2.LINE_AA)
            cv2.putText(overlay, f"KNIGHT({int(kx_norm)},{int(ky_norm)})", (kx_px + 10, ky_px - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 255), 1, lineType=cv2.LINE_AA)

        # 6. Alpha Blending (Grid line transparency: 0.40)
        alpha = 0.40
        annotated = cv2.addWeighted(overlay, alpha, resized, 1 - alpha, 0)
        
        # Keep top/left ruler crisp (100% overlay)
        annotated[0:18, :] = overlay[0:18, :]
        annotated[:, 0:22] = overlay[:, 0:22]

        return annotated
