"""
OhBot Behavior Manager v2
-------------------------
Features:
- Realistic blinking loop started only once
- Idle head/eye movement
- Mood poses: neutral, happy, thrilled, sad, angry, surprise, sideeye
- Heuristic viseme lip-sync during speech
- Micro head/eye motion while speaking
- Safe threading with start/stop behavior manager

Usage:
    python ohbot_behavior_v2.py

Controls are automatic in the demo section at the bottom.
"""

import random
import re
import threading
import time
from dataclasses import dataclass
from typing import Dict, Tuple

from ohbot import ohbot


# -------------------------
# Configuration
# -------------------------

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
    "neutral": MoodPose(
        head_nod=5,
        head_turn=5,
        eye_turn=5,
        eye_tilt=5,
        lid_blink=10,
        top_lip=3,
        bottom_lip=7,
        speech_intensity=1.0,
        speech_speed=1.0,
    ),
    "happy": MoodPose(
        head_nod=7,
        head_turn=5,
        eye_turn=5,
        eye_tilt=7,
        lid_blink=10,
        top_lip=2,
        bottom_lip=9,
        speech_intensity=1.15,
        speech_speed=1.08,
    ),
    "thrilled": MoodPose(
        head_nod=8,
        head_turn=5,
        eye_turn=5,
        eye_tilt=8,
        lid_blink=10,
        top_lip=1,
        bottom_lip=10,
        speech_intensity=1.3,
        speech_speed=1.18,
    ),
    "sad": MoodPose(
        head_nod=2,
        head_turn=4.5,
        eye_turn=5,
        eye_tilt=2,
        lid_blink=8,
        top_lip=7,
        bottom_lip=3,
        speech_intensity=0.75,
        speech_speed=0.82,
    ),
    "angry": MoodPose(
        head_nod=5,
        head_turn=5,
        eye_turn=5,
        eye_tilt=3,
        lid_blink=8,
        top_lip=5,
        bottom_lip=6,
        speech_intensity=1.2,
        speech_speed=1.05,
    ),
    "surprise": MoodPose(
        head_nod=6,
        head_turn=5,
        eye_turn=5,
        eye_tilt=10,
        lid_blink=10,
        top_lip=2,
        bottom_lip=10,
        speech_intensity=1.25,
        speech_speed=1.1,
    ),
    "sideeye": MoodPose(
        head_nod=5,
        head_turn=5,
        eye_turn=9,
        eye_tilt=5,
        lid_blink=8,
        top_lip=4,
        bottom_lip=7,
        speech_intensity=0.9,
        speech_speed=0.95,
    ),
}

# Viseme format: top lip, bottom lip.
# Values are tuned for your existing OhBot direction, where lower TOPLIP and higher BOTTOMLIP
# often look like a more open mouth.
VISEMES: Dict[str, Tuple[float, float]] = {
    "closed": (4, 5),  # M, B, P
    "wide": (2, 9),    # A, I
    "small": (3, 7),   # E
    "round": (3, 8),   # O, U
    "soft": (3, 6),    # general consonants
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


# -------------------------
# Behavior Manager
# -------------------------

class OhBotBehaviorManager:
    def __init__(self):
        self.running = False
        self.speaking = False
        self.current_mood = "neutral"

        self._blink_thread = None
        self._idle_thread = None
        self._lock = threading.RLock()

    # ---------- Basic helpers ----------

    @staticmethod
    def clamp(value: float, low: float = 0, high: float = 10) -> float:
        return max(low, min(high, value))

    def safe_move(self, motor, value: float, speed: int = 5, jitter: float = 0.0):
        """Move a motor safely with optional tiny randomness."""
        value = self.clamp(value + random.uniform(-jitter, jitter))
        try:
            ohbot.move(motor, value, speed)
        except TypeError:
            # Some OhBot library versions may not accept speed.
            ohbot.move(motor, value)

    def move_lips(self, top: float, bottom: float, speed: int = 5, jitter: float = 0.08):
        self.safe_move(ohbot.TOPLIP, top, speed=speed, jitter=jitter)
        self.safe_move(ohbot.BOTTOMLIP, bottom, speed=speed, jitter=jitter)

    # ---------- Mood ----------

    def set_mood(self, mood: str, speed: int = 4):
        with self._lock:
            if mood not in MOODS:
                mood = "neutral"

            self.current_mood = mood
            pose = MOODS[mood]

            self.safe_move(ohbot.HEADNOD, pose.head_nod, speed=speed)
            self.safe_move(ohbot.HEADTURN, pose.head_turn, speed=speed)
            self.safe_move(ohbot.EYETURN, pose.eye_turn, speed=speed)
            self.safe_move(ohbot.EYETILT, pose.eye_tilt, speed=speed)
            self.safe_move(ohbot.LIDBLINK, pose.lid_blink, speed=speed)
            self.move_lips(pose.top_lip, pose.bottom_lip, speed=speed)

    # ---------- Speech/lips ----------

    @staticmethod
    def split_speech(text: str):
        """Split text into small speech chunks and punctuation pauses."""
        parts = re.findall(r"[A-Za-z]+|[,.!?;:]", text)
        chunks = []

        for part in parts:
            if part in PUNCTUATION_PAUSES:
                chunks.append(("pause", part))
            else:
                # Two-character chunks are a good compromise for simple lip motion.
                for i in range(0, len(part), 2):
                    chunks.append(("word", part[i:i + 2]))

        return chunks

    @staticmethod
    def guess_viseme(chunk: str) -> str:
        c = chunk.lower()

        # Closed-mouth sounds first.
        if re.search(r"[mbp]", c):
            return "closed"
        if re.search(r"[ou]", c):
            return "round"
        if re.search(r"[ai]", c):
            return "wide"
        if re.search(r"e", c):
            return "small"
        return "soft"

    def lip_sync_heuristic(self, text: str, mood: str = "neutral"):
        pose = MOODS.get(mood, MOODS["neutral"])
        chunks = self.split_speech(text)

        for kind, value in chunks:
            if not self.speaking:
                break

            if kind == "pause":
                self.move_lips(*VISEMES["rest"], speed=4, jitter=0.05)
                time.sleep(PUNCTUATION_PAUSES.get(value, 0.15))
                continue

            viseme = self.guess_viseme(value)
            top, bottom = VISEMES[viseme]

            # Intensity: push mouth shapes further from rest.
            rest_top, rest_bottom = VISEMES["rest"]
            top = rest_top + (top - rest_top) * pose.speech_intensity
            bottom = rest_bottom + (bottom - rest_bottom) * pose.speech_intensity

            self.move_lips(top, bottom, speed=5, jitter=0.12)

            # Micro motion while speaking. This prevents the robot from looking frozen.
            if random.random() < 0.22:
                self.safe_move(ohbot.HEADNOD, random.uniform(4.4, 5.9), speed=6)

            if random.random() < 0.14:
                self.safe_move(ohbot.HEADTURN, random.uniform(4.6, 5.4), speed=6)

            if random.random() < 0.16:
                self.safe_move(ohbot.EYETURN, random.uniform(4.4, 5.7), speed=6)

            # Faster moods reduce delay. Sad mood slows it down.
            delay = random.uniform(0.055, 0.12) / pose.speech_speed
            time.sleep(delay)

        self.move_lips(*VISEMES["rest"], speed=5, jitter=0.04)

    def expressive_say(self, text: str, mood: str = "neutral", return_to_neutral: bool = True):
        """Speak with mood pose and parallel heuristic mouth animation."""
        with self._lock:
            self.set_mood(mood)
            self.speaking = True

        lip_thread = threading.Thread(
            target=self.lip_sync_heuristic,
            args=(text, mood),
            daemon=True,
        )
        lip_thread.start()

        try:
            ohbot.say(text)
        finally:
            self.speaking = False
            lip_thread.join(timeout=1.0)
            self.move_lips(*VISEMES["rest"], speed=5)

            if return_to_neutral:
                self.set_mood("neutral")

    # ---------- Background loops ----------

    def blink_once(self):
        """One quick natural blink. In this OhBot setup, 0 appears closed and 10 open."""
        self.safe_move(ohbot.LIDBLINK, 0, speed=10)
        time.sleep(random.uniform(0.08, 0.16))
        self.safe_move(ohbot.LIDBLINK, 10, speed=10)

    def blink_loop(self):
        while self.running:
            wait = random.uniform(2.5, 5.8) if not self.speaking else random.uniform(4.5, 8.0)
            time.sleep(wait)

            if not self.running:
                break

            self.blink_once()

            # Occasional double blink.
            if random.random() < 0.12 and not self.speaking:
                time.sleep(random.uniform(0.10, 0.18))
                self.blink_once()

    def idle_motion_loop(self):
        while self.running:
            time.sleep(random.uniform(1.5, 4.0))

            if not self.running:
                break

            if not self.speaking:
                mood = self.current_mood

                # Sideeye should preserve eye direction more often.
                if mood == "sideeye":
                    self.safe_move(ohbot.EYETURN, random.uniform(8.0, 10.0), speed=4)
                else:
                    self.safe_move(ohbot.EYETURN, random.uniform(4.1, 6.0), speed=4)

                self.safe_move(ohbot.HEADTURN, random.uniform(4.2, 5.8), speed=3)
                self.safe_move(ohbot.HEADNOD, random.uniform(4.4, 5.8), speed=3)

    # ---------- Lifecycle ----------

    def start(self):
        if self.running:
            return

        self.running = True
        self.speaking = False

        try:
            ohbot.reset()
        except Exception:
            pass

        self.set_mood("neutral")

        self._blink_thread = threading.Thread(target=self.blink_loop, daemon=True)
        self._idle_thread = threading.Thread(target=self.idle_motion_loop, daemon=True)

        self._blink_thread.start()
        self._idle_thread.start()

    def stop(self):
        self.running = False
        self.speaking = False
        time.sleep(0.2)

        try:
            ohbot.reset()
        finally:
            ohbot.close()


# -------------------------
# Demo
# -------------------------

if __name__ == "__main__":
    bot = OhBotBehaviorManager()

    try:
        bot.start()

        bot.expressive_say("Hello, I am feeling very happy today!", "happy")
        time.sleep(1.5)

        bot.expressive_say("Wow, that is absolutely amazing!", "surprise")
        time.sleep(1.5)

        bot.expressive_say("I do not like this situation.", "angry")
        time.sleep(1.5)

        bot.expressive_say("I feel a little tired now.", "sad")
        time.sleep(1.5)

        bot.set_mood("sideeye")
        time.sleep(1.0)
        bot.expressive_say("Are you sure about that?", "sideeye")
        time.sleep(2.0)

    except KeyboardInterrupt:
        print("Stopping OhBot behavior manager...")

    finally:
        bot.stop()
