"""UI and camera utility functions."""

import time
import cv2


class FPSCounter:
    def __init__(self):
        self.last = time.perf_counter()
        self.fps = 0.0

    def update(self):
        now = time.perf_counter()
        dt = now - self.last
        self.last = now
        if dt > 0:
            instant = 1.0 / dt
            self.fps = 0.9 * self.fps + 0.1 * instant if self.fps else instant
        return self.fps


def draw_text(frame, text, xy, scale=0.65, thickness=2):
    cv2.putText(
        frame, text, xy, cv2.FONT_HERSHEY_SIMPLEX,
        scale, (255, 255, 255), thickness, cv2.LINE_AA
    )


def draw_dashboard(frame, detection, fps, events):
    h, w = frame.shape[:2]

    # Top status panel
    panel_h = 112
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, panel_h), (20, 20, 20), -1)
    frame[:] = cv2.addWeighted(overlay, 0.72, frame, 0.28, 0)

    status = "DROWSY - TAKE A BREAK" if detection.drowsy else (
        "EYES CLOSED" if detection.eyes_closed else
        "YAWNING" if detection.yawning else
        "ALERT"
    )
    status_color = (0, 0, 255) if detection.drowsy else (
        (0, 165, 255) if (detection.eyes_closed or detection.yawning) else (0, 220, 0)
    )

    cv2.putText(frame, status, (20, 42),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 3, cv2.LINE_AA)

    draw_text(frame, f"EAR: {detection.ear:.3f}", (20, 78))
    draw_text(frame, f"MAR: {detection.mar:.3f}", (160, 78))
    draw_text(frame, f"Score: {detection.score}/100", (300, 78))
    draw_text(frame, f"FPS: {fps:.1f}", (470, 78))
    draw_text(frame, f"Events: {events}", (580, 78))

    if detection.face_found:
        x1, y1, x2, y2 = detection.face_box
        box_color = (0, 0, 255) if detection.drowsy else (0, 220, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

    # Bottom instructions
    cv2.rectangle(frame, (0, h - 42), (w, h), (20, 20, 20), -1)
    draw_text(frame, "Q: Quit   R: Reset   S: Save Screenshot", (15, h - 14), 0.55, 1)

    return frame
