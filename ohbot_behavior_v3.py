"""OhBot realistic behavior layer

Only includes the requested behaviors:
1. More realistic lip movement while speaking
2. Different moods: neutral, happy, thrilled, angry, sad, surprise, sideeye
3. Frequent realistic blinking

Usage:
    python ohbot_realistic_behaviors_only.py

Then edit the example lines at the bottom for your own interaction system.
"""

import random
import re
import threading
import time
from ohbot import ohbot


# -------------------------
# Global state
# -------------------------

running = True
speaking = False
current_mood = "neutral"
blink_thread_started = False


# -------------------------
# Mood poses
# Values are 0 to 10
# -------------------------

MOODS = {
    "neutral": {
        "HEADNOD": 5,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 5,
        "LIDBLINK": 10,      # 10 = open on many OhBot setups
        "TOPLIP": 3,
        "BOTTOMLIP": 7,
    },
    "happy": {
        "HEADNOD": 6,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 7,
        "LIDBLINK": 10,
        "TOPLIP": 2,
        "BOTTOMLIP": 9,
    },
    "thrilled": {
        "HEADNOD": 7,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 8,
        "LIDBLINK": 10,
        "TOPLIP": 1,
        "BOTTOMLIP": 10,
    },
    "angry": {
        "HEADNOD": 4,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 3,
        "LIDBLINK": 7,
        "TOPLIP": 5,
        "BOTTOMLIP": 6,
    },
    "sad": {
        "HEADNOD": 2,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 2,
        "LIDBLINK": 8,
        "TOPLIP": 7,
        "BOTTOMLIP": 4,
    },
    "surprise": {
        "HEADNOD": 6,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 9,
        "LIDBLINK": 10,
        "TOPLIP": 2,
        "BOTTOMLIP": 10,
    },
    "sideeye": {
        "HEADNOD": 5,
        "HEADTURN": 5,
        "EYETURN": 9,
        "EYETILT": 4,
        "LIDBLINK": 8,
        "TOPLIP": 4,
        "BOTTOMLIP": 7,
    },
}


# -------------------------
# Viseme-style mouth shapes
# Tuple = top lip, bottom lip
# Tune these if your OhBot lip direction is reversed.
# -------------------------

VISEMES = {
    "closed": (1, 1),   # M, B, P
    "wide":   (2, 10),  # A, I
    "small":  (3, 7),   # E
    "round":  (4, 9),   # O, U
    "soft":   (3, 6),   # normal consonants
    "rest":   (2, 3),
}


MOOD_INTENSITY = {
    "neutral": 1.00,
    "happy": 1.10,
    "thrilled": 1.30,
    "angry": 1.20,
    "sad": 0.75,
    "surprise": 1.25,
    "sideeye": 0.95,
}


# -------------------------
# Helpers
# -------------------------

def clamp(value, low=0, high=10):
    return max(low, min(high, value))


def safe_move(motor, value, speed=5):
    ohbot.move(motor, clamp(value), speed)


def move_lips(top, bottom, speed=5):
    """Move lips with tiny natural randomness."""
    safe_move(ohbot.TOPLIP, top + random.uniform(-0.15, 0.15), speed)
    safe_move(ohbot.BOTTOMLIP, bottom + random.uniform(-0.20, 0.20), speed)


def set_mood(mood="neutral"):
    """Apply one emotional pose."""
    global current_mood

    if mood not in MOODS:
        mood = "neutral"

    current_mood = mood
    m = MOODS[mood]

    safe_move(ohbot.HEADNOD, m["HEADNOD"], 4)
    safe_move(ohbot.HEADTURN, m["HEADTURN"], 4)
    safe_move(ohbot.EYETURN, m["EYETURN"], 4)
    safe_move(ohbot.EYETILT, m["EYETILT"], 4)
    safe_move(ohbot.LIDBLINK, m["LIDBLINK"], 5)
    move_lips(m["TOPLIP"], m["BOTTOMLIP"], 4)


def guess_viseme(chunk):
    """Simple text-to-mouth-shape approximation."""
    c = chunk.lower()

    if re.search(r"[mbp]", c):
        return "closed"
    if re.search(r"[ou]", c):
        return "round"
    if re.search(r"[aiy]", c):
        return "wide"
    if re.search(r"[e]", c):
        return "small"
    return "soft"


def split_speech(text):
    """Break text into small mouth-animation chunks."""
    parts = re.findall(r"[a-zA-Z]+|[,.!?;:]", text)
    chunks = []

    for part in parts:
        if part in ",.!?;:":
            chunks.append(("pause", part))
        else:
            for i in range(0, len(part), 2):
                chunks.append(("word", part[i:i + 2]))

    return chunks


# -------------------------
# Realistic blinking
# -------------------------

def blink_once():
    """One fast natural blink."""
    safe_move(ohbot.LIDBLINK, 0, 10)      # closed
    time.sleep(random.uniform(0.07, 0.14))
    safe_move(ohbot.LIDBLINK, 10, 10)     # open


def blink_loop():
    """Frequent realistic blinking. Starts once only."""
    while running:
        if speaking:
            wait_time = random.uniform(3.5, 6.5)
        else:
            wait_time = random.uniform(2.0, 4.5)

        time.sleep(wait_time)
        blink_once()

        # occasional natural double blink
        if random.random() < 0.12:
            time.sleep(random.uniform(0.12, 0.22))
            blink_once()


def start_blinking():
    global blink_thread_started

    if not blink_thread_started:
        blink_thread_started = True
        threading.Thread(target=blink_loop, daemon=True).start()


# -------------------------
# Realistic speaking / lips
# -------------------------

def lip_sync_heuristic(text, mood="neutral"):
    """Animate lips while ohbot.say() is speaking.

    This is not true phoneme timing, but it is much better than simple
    random opening/closing because it uses rough viseme shapes.
    """
    intensity = MOOD_INTENSITY.get(mood, 1.0)
    chunks = split_speech(text)

    for kind, value in chunks:
        if not speaking:
            break

        if kind == "pause":
            move_lips(*VISEMES["rest"], speed=4)
            time.sleep(random.uniform(0.12, 0.24))
            continue

        viseme = guess_viseme(value)
        top, bottom = VISEMES[viseme]

        # Keep closed sounds closed; scale only open mouth shapes.
        if viseme != "closed":
            top = 5 + (top - 5) * intensity
            bottom = 5 + (bottom - 5) * intensity

        move_lips(top, bottom, speed=5)

        # Tiny head/eye micro-motions during speech.
        if random.random() < 0.18:
            safe_move(ohbot.HEADNOD, random.uniform(4.5, 5.8), 6)
        if random.random() < 0.12:
            safe_move(ohbot.EYETURN, random.uniform(4.4, 5.6), 6)

        # Variable timing feels less robotic.
        time.sleep(random.uniform(0.055, 0.12))

    move_lips(*VISEMES["rest"], speed=5)


def expressive_say(text, mood="neutral", return_to_neutral=True):
    """Speak with mood, blinking, and realistic lip movement."""
    global speaking

    start_blinking()
    set_mood(mood)

    speaking = True
    lip_thread = threading.Thread(
        target=lip_sync_heuristic,
        args=(text, mood),
        daemon=True,
    )
    lip_thread.start()

    ohbot.say(text)

    speaking = False
    lip_thread.join(timeout=1.0)

    if return_to_neutral:
        set_mood("neutral")


# -------------------------
# Shutdown
# -------------------------

def stop_behaviors():
    global running, speaking
    speaking = False
    running = False
    time.sleep(0.3)
    ohbot.reset()
    ohbot.close()


# -------------------------
# Example usage
# -------------------------

if __name__ == "__main__":
    try:
        ohbot.reset()
        start_blinking()

        expressive_say("Hello, I am feeling very happy today!", "happy")
        time.sleep(1)

        expressive_say("Wow, that is absolutely amazing!", "thrilled")
        time.sleep(1)

        expressive_say("I do not like this situation.", "angry")
        time.sleep(1)

        expressive_say("I feel a little tired now.", "sad")
        time.sleep(1)

        expressive_say("Oh! I did not expect that!", "surprise")
        time.sleep(3)

    finally:
        stop_behaviors()
