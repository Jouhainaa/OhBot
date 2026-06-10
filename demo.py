import time

from OhBotProject.behavior.behavior_engine import OhBotBehaviorManager


def run_demo():
    mgr = OhBotBehaviorManager()

    print("Starting OhBot behavior manager (blink loop active)...")
    mgr.start()

    try:
        # 1) Blinking: let the blink loop run for a few seconds
        print("Demo: blinking (watch the robot blink) for 4 seconds...")
        time.sleep(10)

        # 2) Emotions: cycle through several moods
        emotions = ["happy", "surprise", "sad", "angry"]
        print("Demo: showing emotions")
        for e in emotions:
            print(f" Setting mood: {e}")
            mgr.set_mood(e)
            time.sleep(10)

        # 3) Simple speaking: short expressive phrase
        print("Demo: simple speaking")
        mgr.expressive_say("Hello! I am OhBot. Nice to meet you.", mood="happy")
        time.sleep(1)

        # 4) Comedian: tell a short joke (uses ComedyGenerator)
        print("Demo: comedian — telling a short joke")
        mgr.tell_joke()
        time.sleep(1)

    except KeyboardInterrupt:
        print("Demo interrupted by user")
    finally:
        print("Stopping OhBot and cleaning up...")
        mgr.stop()


if __name__ == "__main__":
    run_demo()
