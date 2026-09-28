"""Facial metric calculations."""

import math
from typing import Sequence, Tuple


Point = Tuple[float, float]


def euclidean(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def eye_aspect_ratio(eye: Sequence[Point]) -> float:
    """Calculate EAR from 6 ordered eye points."""
    if len(eye) != 6:
        raise ValueError("EAR requires exactly 6 points.")
    vertical_1 = euclidean(eye[1], eye[5])
    vertical_2 = euclidean(eye[2], eye[4])
    horizontal = euclidean(eye[0], eye[3])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def mouth_aspect_ratio(mouth: Sequence[Point]) -> float:
    """Calculate MAR from 6 mouth points."""
    if len(mouth) != 6:
        raise ValueError("MAR requires exactly 6 points.")
    vertical_1 = euclidean(mouth[1], mouth[5])
    vertical_2 = euclidean(mouth[2], mouth[4])
    horizontal = euclidean(mouth[0], mouth[3])
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
