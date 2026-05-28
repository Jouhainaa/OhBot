import time

from behavior.mood_controller import set_mood
from behavior.speech_controller import expressive_say
from behavior.blink_controller import start_blinking, stop_blinking
from behavior.gesture_controller import do_gesture
from behavior.ai_controller import ask_chatgpt


class BehaviorEngine:
    def __init__(self):
        self.is_running = False

    def start(self):
        """
        Starts background behaviors like blinking.
        """
        self.is_running = True
        start_blinking()
        set_mood("neutral")

    def say_with_behavior(self, text, mood="neutral", gesture=None):
        """
        Makes OhBot speak with a mood and optional gesture.
        """
        set_mood(mood)

        if gesture is not None:
            do_gesture(gesture)

        expressive_say(text, mood)

        set_mood("neutral")

    def respond(self, user_input):
        result = ask_chatgpt(user_input)

        answer = result["answer"]
        mood = result["mood"]
        gesture = result["gesture"]

        if gesture == "none":
            gesture = None

        self.say_with_behavior(answer, mood, gesture)

    def choose_gesture(self, mood):
        """
        Selects a simple gesture based on the mood.
        """
        if mood == "happy":
            return "nod"
        elif mood == "thrilled":
            return "excited"
        elif mood == "sad":
            return "sad_look"
        elif mood == "angry":
            return "angry_look"
        elif mood == "surprise":
            return "surprised"
        elif mood == "sideeye":
            return "sideeye"

        return None

    def stop(self):
        """
        Stops all behavior systems.
        """
        self.is_running = False
        stop_blinking()
        set_mood("neutral")