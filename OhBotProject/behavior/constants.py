import random
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class MoodPose:
    head_nod: float
    head_turn: float
    eye_turn: float
    eye_tilt: float
    lid_blink: float
    top_lip: float
    bottom_lip: float
    speech_intensity: float = 1.0
    speech_speed: float = 1.0


MOODS: Dict[str, MoodPose] = {
    "neutral": MoodPose(5, 5, 5, 5, 10, 3, 7, 1.0, 1.0),
    "happy": MoodPose(7, 5, 5, 7, 10, 2, 9, 1.15, 1.08),
    "thrilled": MoodPose(8, 5, 5, 8, 10, 1, 10, 1.3, 1.18),
    "sad": MoodPose(2, 4.5, 5, 2, 8, 7, 3, 0.75, 0.82),
    "angry": MoodPose(6, 5, 5, 3, 5, 6, 2, 1.2, 1.05),
    "surprise": MoodPose(6, 5, 5, 10, 10, 9, 10, 1.25, 1.1),
    "sideeye": MoodPose(5, 5, 9, 5, 8, 4, 7, 0.9, 0.95),
}


# Viseme format: top lip, bottom lip.
VISEMES: Dict[str, Tuple[float, float]] = {
    "closed": (4, 5),
    "wide": (2, 9),
    "small": (3, 7),
    "round": (3, 8),
    "soft": (3, 6),
    "rest": (3, 7),
}


PUNCTUATION_PAUSES = {
    ",": 0.14,
    ";": 0.18,
    ":": 0.18,
    ".": 0.28,
    "!": 0.30,
    "?": 0.32,
}
