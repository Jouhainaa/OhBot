import time

from ohbot import ohbot
from behavior.mood_controller import safe_move


def do_gesture(gesture_name):
    if gesture_name == "nod":
        nod()

    elif gesture_name == "excited":
        excited()

    elif gesture_name == "sad_look":
        sad_look()

    elif gesture_name == "angry_look":
        angry_look()

    elif gesture_name == "surprised":
        surprised()

    elif gesture_name == "sideeye":
        sideeye()


def nod():
    safe_move(ohbot.HEADNOD, 7, 5)
    time.sleep(0.25)
    safe_move(ohbot.HEADNOD, 4, 5)
    time.sleep(0.25)
    safe_move(ohbot.HEADNOD, 5, 5)


def excited():
    safe_move(ohbot.HEADNOD, 7, 7)
    safe_move(ohbot.EYETILT, 8, 7)
    time.sleep(0.25)

    safe_move(ohbot.HEADTURN, 4, 7)
    time.sleep(0.2)

    safe_move(ohbot.HEADTURN, 6, 7)
    time.sleep(0.2)

    safe_move(ohbot.HEADTURN, 5, 7)
    safe_move(ohbot.HEADNOD, 5, 7)


def sad_look():
    safe_move(ohbot.HEADNOD, 2, 4)
    safe_move(ohbot.EYETILT, 2, 4)
    time.sleep(0.5)


def angry_look():
    safe_move(ohbot.HEADNOD, 4, 6)
    safe_move(ohbot.EYETILT, 3, 6)
    safe_move(ohbot.LIDBLINK, 6, 6)
    time.sleep(0.4)


def surprised():
    safe_move(ohbot.HEADNOD, 7, 7)
    safe_move(ohbot.EYETILT, 9, 7)
    safe_move(ohbot.LIDBLINK, 10, 8)
    time.sleep(0.4)


def sideeye():
    safe_move(ohbot.EYETURN, 9, 5)
    time.sleep(0.6)
    safe_move(ohbot.EYETURN, 5, 5)