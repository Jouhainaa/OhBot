import random
import re
import threading
import time
from ohbot import ohbot

running = True
current_mood = "neutral"
speaking = False

MOODS = {
    "neutral":  {"HEADNOD": 5, "HEADTURN": 5, "EYETURN": 5, "EYETILT": 5, 'LIDBLINK': 5, 'TOPLIP': 5, 'BOTTOMLIP': 5},
    "happy":  {"HEADNOD": 7, "HEADTURN": 5, "EYETURN": 5, "EYETILT": 5, 'LIDBLINK': 8, 'TOPLIP': 0, 'BOTTOMLIP': 10},
    "sad":  {"HEADNOD": 1, "HEADTURN": 4, "EYETURN": 5, "EYETILT": 2, 'LIDBLINK': 8, 'TOPLIP': 8, 'BOTTOMLIP': 1},
    "angry":  {"HEADNOD": 5, "HEADTURN": 5, "EYETURN": 5, "EYETILT": 5, 'LIDBLINK': 6, 'TOPLIP': 6, 'BOTTOMLIP': 5},
    "surprise":  {"HEADNOD": 5, "HEADTURN": 5, "EYETURN": 5, "EYETILT": 10, 'LIDBLINK': 10, 'TOPLIP': 7, 'BOTTOMLIP': 7},
    "sideeye":  {"HEADNOD": 5, "HEADTURN": 5, "EYETURN": 10, "EYETILT": 5, 'LIDBLINK': 5, 'TOPLIP': 5, 'BOTTOMLIP': 5},

}

    # looks happy "happy":    {"head": 7, "turn": 5, "eye": 5, "tilt": 10},


VISEMES = {
    "closed": (4, 5),   # M, B, P
    "wide":   (7, 7),   # A, I
    "small":  (2, 7),   # E
    "round":  (3, 7),   # O, U
    "soft":   (2, 6),   # normal consonants
    "rest":   (3, 7),
}

def clamp(x):
    return max(0, min(10, x))

def move_lips(top, bottom, speed=5):
    ohbot.move(ohbot.TOPLIP, clamp(top + random.uniform(-0.1, 0.1)), speed)
    ohbot.move(ohbot.BOTTOMLIP, clamp(bottom + random.uniform(-0.1, 0.1)), speed)

def set_mood(mood):
    global current_mood
    current_mood = mood

    m = MOODS.get(mood, MOODS["neutral"])

    ohbot.move(ohbot.HEADNOD, m["HEADNOD"], 4)
    ohbot.move(ohbot.HEADTURN, m["HEADTURN"], 4)
    ohbot.move(ohbot.EYETURN, m["EYETURN"], 4)
    ohbot.move(ohbot.EYETILT, m["EYETILT"], 4)
    ohbot.move(ohbot.LIDBLINK, m["LIDBLINK"], 4)
    ohbot.move(ohbot.TOPLIP, m["TOPLIP"], 4)
    ohbot.move(ohbot.BOTTOMLIP, m["BOTTOMLIP"], 4)



def guess_viseme(chunk):
    c = chunk.lower()

    if re.search(r"[mbp]", c):
        return "closed"
    if re.search(r"[ou]", c):
        return "round"
    if re.search(r"[ai]", c):
        return "wide"
    if re.search(r"[e]", c):
        return "small"
    return "soft"

def split_speech(text):
    parts = re.findall(r"[a-zA-Z]+|[,.!?;:]", text)
    chunks = []

    for part in parts:
        if part in ",.!?;:":
            chunks.append(("pause", part))
        else:
            # split long words into smaller mouth units
            for i in range(0, len(part), 2):
                chunks.append(("word", part[i:i+2]))

    return chunks

def lip_sync_heuristic(text, mood="neutral"):
    global speaking

    intensity = {
        "neutral": 1.0,
        "happy": 1.15,
        "thrilled": 1.35,
        "angry": 1.25,
        "sad": 0.75,
    }.get(mood, 1.0)

    chunks = split_speech(text)

    for kind, value in chunks:
        if not speaking:
            break

        if kind == "pause":
            move_lips(*VISEMES["rest"], speed=4)
            time.sleep(0.12)
            continue

        viseme = guess_viseme(value)
        top, bottom = VISEMES[viseme]

        # top *= intensity
        # bottom *= intensity

        move_lips(top, bottom, speed=4)

        # tiny head movement while speaking
        if random.random() < 0.25:
            ohbot.move(ohbot.HEADNOD, random.uniform(4.3, 5.8), 6)

        time.sleep(random.uniform(0.07, 0.13))

    move_lips(*VISEMES["rest"], speed=4)

def blink_loop():
    while running:
        # blink less often while speaking
        wait = random.uniform(2, 3) if not speaking else random.uniform(3, 4)
        time.sleep(wait)

        ohbot.move(ohbot.LIDBLINK, 0)
        time.sleep(random.uniform(0.3, 0.4))
        ohbot.move(ohbot.LIDBLINK, 10)

        # occasional double blink
        # if random.random() < 0.15:
        #     time.sleep(0.12)
        #     ohbot.move(ohbot.LIDBLINK, 10, 10)
        #     time.sleep(0.08)
        #     ohbot.move(ohbot.LIDBLINK, 0, 10)

def idle_motion_loop():
    while running:
        time.sleep(random.uniform(1.5, 4.5))

        if not speaking:
            ohbot.move(ohbot.HEADTURN, random.uniform(4.2, 5.8), 3)
            ohbot.move(ohbot.EYETURN, random.uniform(4.0, 6.0), 4)
            ohbot.move(ohbot.HEADNOD, random.uniform(4.5, 5.7), 3)
            # ohbot.move(ohbot.LIDBLINK, 0)
            # time.sleep(random.uniform(0.2, 0.4))
            # ohbot.move(ohbot.LIDBLINK, 10)


def expressive_say(text, mood="neutral"):
    global speaking

    set_mood(mood)
    speaking = True

    threading.Thread(target=blink_loop, daemon=True).start()
    lip_thread = threading.Thread(
        target=lip_sync_heuristic,
        args=(text, mood),
        daemon=True
    )
    lip_thread.start()

    ohbot.say(text)

    speaking = False
    lip_thread.join(timeout=1)

    # move_lips(*VISEMES["rest"], speed=5)
    # set_mood("neutral")

def start_behavior():
    threading.Thread(target=blink_loop, daemon=True).start()
    # threading.Thread(target=idle_motion_loop, daemon=True).start()

def stop_behavior():
    global running
    running = False
    ohbot.reset()
    ohbot.close()


# -------------------------
# Example usage
# -------------------------

ohbot.reset()

# ohbot.move(ohbot.TOPLIP, 3)
# ohbot.move(ohbot.BOTTOMLIP, 7)

# exit()
# start_behavior()
expressive_say("Hello, I am feeling very happy today!", "happy")
time.sleep(3)
expressive_say("Wow, that is absolutely amazing!", "surprise")
time.sleep(3)
expressive_say("I do not like this situation.", "angry")
time.sleep(3)
expressive_say("I feel a little tired now.", "sad")
time.sleep(10)

stop_behavior()

