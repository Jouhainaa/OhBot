import random
import threading
import time

from ohbot import ohbot
from behavior.mood_controller import safe_move


running = False
blink_thread_started = False
speaking = False


def set_speaking_state(state):
    """
    Tells the blink system whether OhBot is currently speaking.
    """
    global speaking
    speaking = state


def blink_once():
    """
    Performs one quick natural blink.
    """
    safe_move(ohbot.LIDBLINK, 0, 10)
    time.sleep(random.uniform(0.07, 0.14))
    safe_move(ohbot.LIDBLINK, 10, 10)


def blink_loop():
    """
    Runs in the background and makes OhBot blink naturally.
    """
    global running

    while running:
        if speaking:
            wait_time = random.uniform(3.5, 6.5)
        else:
            wait_time = random.uniform(2.0, 4.5)

        time.sleep(wait_time)

        if running:
            blink_once()

        if running and random.random() < 0.12:
            time.sleep(random.uniform(0.12, 0.22))
            blink_once()


def start_blinking():
    """
    Starts blinking in a background thread.
    """
    global running, blink_thread_started

    if not blink_thread_started:
        running = True
        blink_thread_started = True

        thread = threading.Thread(target=blink_loop, daemon=True)
        thread.start()


def stop_blinking():
    """
    Stops the blinking loop.
    """
    global running, blink_thread_started

    running = False
    blink_thread_started = False