"""MediaPipe facial-landmark detector and drowsiness state machine."""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import time

import cv2
import mediapipe as mp

from config import (
    EAR_THRESHOLD,
    EYE_CLOSED_SECONDS,
    MAR_THRESHOLD,
    YAWN_SECONDS,
    MAX_NUM_FACES,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)
from .metrics import eye_aspect_ratio, mouth_aspect_ratio, clamp


# MediaPipe Face Mesh landmark indices.
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH = [78, 81, 13, 308, 14, 178]


@dataclass
class DetectionResult:
    face_found: bool = False
    left_ear: float = 0.0
    right_ear: float = 0.0
    ear: float = 0.0
    mar: float = 0.0
    eyes_closed: bool = False
    yawning: bool = False
    eye_closed_duration: float = 0.0
    yawn_duration: float = 0.0
    drowsy: bool = False
    score: int = 0
    reason: str = "No face detected"
    face_box: Optional[Tuple[int, int, int, int]] = None
    landmarks: Optional[List[Tuple[int, int]]] = None


class DrowsinessDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=MAX_NUM_FACES,
            refine_landmarks=True,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self.eye_closed_start: Optional[float] = None
        self.yawn_start: Optional[float] = None

    def reset(self):
        self.eye_closed_start = None
        self.yawn_start = None

    def process(self, frame) -> DetectionResult:
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self.mesh.process(rgb)

        if not result.multi_face_landmarks:
            self.reset()
            return DetectionResult()

        face = result.multi_face_landmarks[0]
        points = [
            (int(lm.x * w), int(lm.y * h))
            for lm in face.landmark
        ]

        left = [points[i] for i in LEFT_EYE]
        right = [points[i] for i in RIGHT_EYE]
        mouth = [points[i] for i in MOUTH]

        left_ear = eye_aspect_ratio(left)
        right_ear = eye_aspect_ratio(right)
        ear = (left_ear + right_ear) / 2.0
        mar = mouth_aspect_ratio(mouth)

        now = time.monotonic()

        eyes_closed = ear < EAR_THRESHOLD
        yawning = mar > MAR_THRESHOLD

        if eyes_closed:
            if self.eye_closed_start is None:
                self.eye_closed_start = now
            eye_duration = now - self.eye_closed_start
        else:
            self.eye_closed_start = None
            eye_duration = 0.0

        if yawning:
            if self.yawn_start is None:
                self.yawn_start = now
            yawn_duration = now - self.yawn_start
        else:
            self.yawn_start = None
            yawn_duration = 0.0

        eye_factor = clamp(eye_duration / EYE_CLOSED_SECONDS, 0, 1)
        yawn_factor = clamp(yawn_duration / YAWN_SECONDS, 0, 1)

        score = 0
        if eyes_closed:
            score += 35
        if eye_duration >= EYE_CLOSED_SECONDS:
            score += 50
        elif eye_duration > 0.4:
            score += 20

        if yawning:
            score += 20
        if yawn_duration >= YAWN_SECONDS:
            score += 20

        score = min(100, score)

        drowsy = eye_duration >= EYE_CLOSED_SECONDS or (
            score >= 70 and (eyes_closed or yawning)
        )

        if drowsy:
            if eye_duration >= EYE_CLOSED_SECONDS:
                reason = "Eyes closed too long"
            else:
                reason = "Drowsiness indicators detected"
        elif eyes_closed:
            reason = "Eyes closing"
        elif yawning:
            reason = "Possible yawn"
        else:
            reason = "Alert"

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        box = (max(0, min(xs)), max(0, min(ys)),
               min(w, max(xs)), min(h, max(ys)))

        return DetectionResult(
            face_found=True,
            left_ear=left_ear,
            right_ear=right_ear,
            ear=ear,
            mar=mar,
            eyes_closed=eyes_closed,
            yawning=yawning,
            eye_closed_duration=eye_duration,
            yawn_duration=yawn_duration,
            drowsy=drowsy,
            score=score,
            reason=reason,
            face_box=box,
            landmarks=points,
        )

    def close(self):
        self.mesh.close()
