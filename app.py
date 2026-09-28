"""Driver Drowsiness Detection - main application."""

from pathlib import Path
import time

import cv2

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    WINDOW_NAME,
    MIRROR_CAMERA,
)
from src.detector import DrowsinessDetector
from src.alarm import Alarm
from src.logger import EventLogger
from src.utils import FPSCounter, draw_dashboard


def open_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(CAMERA_INDEX)

    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    return cap


def main():
    cap = open_camera()
    if not cap.isOpened():
        raise RuntimeError(
            "Could not open webcam. Check camera permissions, camera connection, "
            "and CAMERA_INDEX in config.py."
        )

    detector = DrowsinessDetector()
    alarm = Alarm()
    logger = EventLogger()
    fps_counter = FPSCounter()

    event_count = 0
    last_event_time = 0.0
    running = True

    print("=" * 60)
    print(" DRIVER DROWSINESS DETECTION SYSTEM")
    print("=" * 60)
    print("Q = Quit | R = Reset | S = Save screenshot")
    print("Keep your face visible and ensure reasonable lighting.")
    print("=" * 60)

    try:
        while running:
            ok, frame = cap.read()
            if not ok:
                print("Unable to read a frame from the webcam.")
                break

            if MIRROR_CAMERA:
                frame = cv2.flip(frame, 1)

            detection = detector.process(frame)
            fps = fps_counter.update()

            now = time.monotonic()

            if detection.drowsy:
                alarm.trigger()

                # Avoid writing hundreds of events during one prolonged alert.
                if now - last_event_time >= 8.0:
                    logger.log_event(frame, detection)
                    event_count += 1
                    last_event_time = now

            display = draw_dashboard(frame, detection, fps, event_count)
            cv2.imshow(WINDOW_NAME, display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                running = False
            elif key == ord("r"):
                detector.reset()
                last_event_time = 0.0
                print("Detection state reset.")
            elif key == ord("s"):
                stamp = time.strftime("%Y%m%d_%H%M%S")
                path = Path("logs") / f"manual_{stamp}.jpg"
                cv2.imwrite(str(path), frame)
                print(f"Saved screenshot: {path}")

    finally:
        detector.close()
        alarm.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
