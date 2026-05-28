import random
from ohbot import ohbot


# -------------------------
# Mood Definitions
# Values between 0 and 10
# -------------------------

MOODS = {
    "neutral": {
        "HEADNOD": 5,
        "HEADTURN": 5,
        "EYETURN": 5,
        "EYETILT": 5,
        "LIDBLINK": 10,
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
# Helper Functions
# -------------------------

def clamp(value, low=0, high=10):
    return max(low, min(high, value))


def safe_move(motor, value, speed=5):
    """
    Safely moves a motor while keeping values valid.
    """
    ohbot.move(motor, clamp(value), speed)


def move_lips(top, bottom, speed=5):
    """
    Moves lips with tiny randomness for realism.
    """
    safe_move(
        ohbot.TOPLIP,
        top + random.uniform(-0.15, 0.15),
        speed
    )

    safe_move(
        ohbot.BOTTOMLIP,
        bottom + random.uniform(-0.20, 0.20),
        speed
    )


# -------------------------
# Main Mood Function
# -------------------------

def set_mood(mood="neutral"):
    """
    Applies an emotional pose to OhBot.
    """

    if mood not in MOODS:
        mood = "neutral"

    m = MOODS[mood]

    safe_move(ohbot.HEADNOD, m["HEADNOD"], 4)
    safe_move(ohbot.HEADTURN, m["HEADTURN"], 4)

    safe_move(ohbot.EYETURN, m["EYETURN"], 4)
    safe_move(ohbot.EYETILT, m["EYETILT"], 4)

    safe_move(ohbot.LIDBLINK, m["LIDBLINK"], 5)

    move_lips(m["TOPLIP"], m["BOTTOMLIP"], 4)