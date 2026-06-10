import random
import re
import threading
import time
from typing import Optional

from ohbot import ohbot

from .constants import MOODS, VISEMES, PUNCTUATION_PAUSES
from .comedy_generator import ComedyGenerator

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except Exception as e:
    print(e)
    SPEECH_RECOGNITION_AVAILABLE = False


class OhBotBehaviorManager:
    def __init__(self):
        self.running = False
        self.speaking = False
        self.current_mood = "neutral"

        self._blink_thread = None
        self._idle_thread = None
        self._lock = threading.RLock()

        self.comedy_generator = ComedyGenerator()

    # ---------- Basic helpers ----------

    @staticmethod
    def clamp(value: float, low: float = 0, high: float = 10) -> float:
        return max(low, min(high, value))

    def safe_move(self, motor, value: float, speed: int = 5, jitter: float = 0.0):
        value = self.clamp(value + random.uniform(-jitter, jitter))
        try:
            ohbot.move(motor, value, speed)
        except TypeError:
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
        parts = re.findall(r"[A-Za-z]+|[,.!?;:]", text)
        chunks = []

        for part in parts:
            if part in PUNCTUATION_PAUSES:
                chunks.append(("pause", part))
            else:
                for i in range(0, len(part), 2):
                    chunks.append(("word", part[i:i + 2]))

        return chunks

    @staticmethod
    def guess_viseme(chunk: str) -> str:
        c = chunk.lower()
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

            rest_top, rest_bottom = VISEMES["rest"]
            top = rest_top + (top - rest_top) * pose.speech_intensity
            bottom = rest_bottom + (bottom - rest_bottom) * pose.speech_intensity

            self.move_lips(top, bottom, speed=5, jitter=0.12)

            if random.random() < 0.22:
                self.safe_move(ohbot.HEADNOD, random.uniform(4.4, 5.9), speed=6)

            if random.random() < 0.14:
                self.safe_move(ohbot.HEADTURN, random.uniform(4.6, 5.4), speed=6)

            if random.random() < 0.16:
                self.safe_move(ohbot.EYETURN, random.uniform(4.4, 5.7), speed=6)

            delay = random.uniform(0.055, 0.12) / pose.speech_speed
            time.sleep(delay)

        self.move_lips(*VISEMES["rest"], speed=5, jitter=0.04)

    def expressive_say(self, text: str, mood: str = "neutral", return_to_neutral: bool = True):
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

    def tell_joke(self, topic: Optional[str] = None, style: str = "basic"):
        joke_parts = self.comedy_generator.generate_joke_with_emotions(topic=topic, style=style)

        for sentence, emotion in joke_parts:
            print(f"[{emotion.upper()}] {sentence}")
            self.expressive_say(sentence, mood=emotion, return_to_neutral=False)
            time.sleep(0.5)

        self.set_mood("neutral")

    def listen_for_speech(self, timeout: int = 10) -> Optional[str]:
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("Speech recognition not available. Install: pip install SpeechRecognition")
            return None

        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                self.set_mood("surprise")
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=timeout)

            print("Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()

        except Exception as e:
            try:
                self.expressive_say("Sorry, I didn't catch that!", "sad")
            except Exception:
                pass
            return None

    # ---------- Background loops ----------

    def blink_once(self):
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
