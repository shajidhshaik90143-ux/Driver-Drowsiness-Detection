"""CSV event logger and screenshot evidence storage."""

from pathlib import Path
from datetime import datetime
import csv
import cv2


class EventLogger:
    def __init__(self, base_dir="logs"):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        self.events_dir = self.base / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.base / "drowsiness_events.csv"

        if not self.csv_path.exists():
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "score",
                    "ear",
                    "mar",
                    "eye_closed_seconds",
                    "yawn_seconds",
                    "reason",
                    "screenshot",
                ])

    def log_event(self, frame, detection):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        screenshot = self.events_dir / f"drowsiness_{stamp}.jpg"
        cv2.imwrite(str(screenshot), frame)

        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                detection.score,
                f"{detection.ear:.4f}",
                f"{detection.mar:.4f}",
                f"{detection.eye_closed_duration:.2f}",
                f"{detection.yawn_duration:.2f}",
                detection.reason,
                str(screenshot),
            ])

        return screenshot
