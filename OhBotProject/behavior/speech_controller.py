import random
import re
import threading
import time

from ohbot import ohbot
from behavior.mood_controller import safe_move, move_lips
from behavior.blink_controller import set_speaking_state


VISEMES = {
    "closed": (1, 1),
    "wide": (2, 10),
    "small": (3, 7),
    "round": (4, 9),
    "soft": (3, 6),
    "rest": (2, 3),
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


def guess_viseme(chunk):
    """
    Guesses a mouth shape from letters.
    """
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
    """
    Splits text into small chunks for lip animation.
    """
    parts = re.findall(r"[a-zA-Z]+|[,.!?;:]", text)
    chunks = []

    for part in parts:
        if part in ",.!?;:":
            chunks.append(("pause", part))
        else:
            for i in range(0, len(part), 2):
                chunks.append(("word", part[i:i + 2]))

    return chunks


def lip_sync_heuristic(text, mood="neutral"):
    """
    Moves OhBot lips while speaking.
    This is not perfect phoneme timing, but looks more realistic
    than random mouth movement.
    """
    intensity = MOOD_INTENSITY.get(mood, 1.0)
    chunks = split_speech(text)

    for kind, value in chunks:
        viseme = None

        if kind == "pause":
            move_lips(*VISEMES["rest"], speed=4)
            time.sleep(random.uniform(0.12, 0.24))
            continue

        viseme = guess_viseme(value)
        top, bottom = VISEMES[viseme]

        if viseme != "closed":
            top = 5 + (top - 5) * intensity
            bottom = 5 + (bottom - 5) * intensity

        move_lips(top, bottom, speed=8)

        if random.random() < 0.18:
            safe_move(ohbot.HEADNOD, random.uniform(4.5, 5.8), 6)

        if random.random() < 0.12:
            safe_move(ohbot.EYETURN, random.uniform(4.4, 5.6), 6)

        time.sleep(random.uniform(0.055, 0.12))

    move_lips(*VISEMES["rest"], speed=5)


def expressive_say(text, mood="neutral"):
    """
    Speaks with lip movement while OhBot is talking.
    """
    set_speaking_state(True)

    lip_thread = threading.Thread(
        target=lip_sync_heuristic,
        args=(text, mood),
        daemon=True
    )

    lip_thread.start()

    ohbot.say(text)

    set_speaking_state(False)
    lip_thread.join(timeout=2.0)

    move_lips(*VISEMES["rest"], speed=5)

def natural_head_motion(mood="neutral"):
    """
    Small natural head movements while speaking.
    """
    for _ in range(6):
        if mood == "happy":
            safe_move(ohbot.HEADNOD, random.uniform(5.2, 6.5), 5)
            safe_move(ohbot.HEADTURN, random.uniform(4.5, 5.5), 5)

        elif mood == "sad":
            safe_move(ohbot.HEADNOD, random.uniform(2.5, 4.0), 4)
            safe_move(ohbot.HEADTURN, random.uniform(4.7, 5.3), 4)

        elif mood == "sideeye":
            safe_move(ohbot.EYETURN, random.uniform(7.0, 9.0), 4)
            safe_move(ohbot.HEADTURN, random.uniform(4.0, 5.0), 4)

        elif mood == "surprise":
            safe_move(ohbot.HEADNOD, random.uniform(6.0, 7.5), 6)
            safe_move(ohbot.EYETILT, random.uniform(7.0, 9.0), 6)

        else:
            safe_move(ohbot.HEADNOD, random.uniform(4.5, 5.8), 5)
            safe_move(ohbot.HEADTURN, random.uniform(4.4, 5.6), 5)

        time.sleep(random.uniform(0.25, 0.45))