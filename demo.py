import time

from OhBotProject.behavior.behavior_engine import OhBotBehaviorManager


def run_demo():
    mgr = OhBotBehaviorManager()

    print("Starting OhBot behavior manager (blink loop active)...")
    mgr.start()

    try:
        # 1) Blinking: let the blink loop run for a few seconds
        print("Demo: blinking (watch the robot blink) for 4 seconds...")
        mgr.expressive_say("Hello! I am OhBot. This is me just blinking.", mood="neutral")
        time.sleep(10)

        # 2) Emotions: cycle through several moods
        emotions = ["happy", "surprise", "sad", "angry"]
        print("Demo: showing emotions")
        mgr.expressive_say("Now, I will show some emotions. Don`t call me dramatic.", mood="neutral")
        for e in emotions:
            print(f" Setting mood: {e}")
            mgr.expressive_say(f"This is me being {e}.", mood=e)
            time.sleep(1)
            mgr.set_mood(e)
            time.sleep(5)

        # 3) Simple speaking: short expressive phrase
        print("Demo: simple speaking")
        mgr.expressive_say("Now, Lets stop being dramatic and let me tell you some jokes.", mood="happy")
        time.sleep(1)

        # Minimal interactive prompt preserved from original script
        print("\n=== OhBot Stand-up Comedian ===")
        print("1. Interactive Mode (you provide topics)")
        print("2. Automatic Mode (pre-set comedy routine)")

        try:
            choice = input("Choose mode (1 or 2): ").strip()
        except EOFError:
            choice = "2"

        if choice == "1":
            # Interactive mode: allow voice or keyboard topic input; only basic jokes.
            num_jokes = 3
            try:
                num_input = input("How many jokes would you like? (default 3): ").strip()
                if num_input:
                    num_jokes = int(num_input)
            except (ValueError, EOFError):
                pass

            # Choose input method
            try:
                method = input("Input method — (v)oice or (k)eyboard? (default k): ").strip().lower()
            except EOFError:
                method = "k"

            use_voice = method == "v"
            if use_voice:
                print("Using voice input for topics. Make sure your microphone is active.")
            else:
                print("Using keyboard input for topics.")

            for i in range(num_jokes):
                topic = None

                if use_voice:
                    mgr.expressive_say("Please say a topic for the next joke.", "neutral")
                    print(f"Listening for topic #{i+1} (timeout 8s)...")
                    topic_heard = mgr.listen_for_speech(timeout=8)
                    if topic_heard:
                        topic = topic_heard
                        print(f"Heard topic: {topic}")
                    else:
                        print("No voice input detected — falling back to keyboard.")
                        try:
                            topic_in = input(f"Enter topic for joke #{i+1} (leave blank for random): ").strip()
                        except EOFError:
                            topic_in = ""
                        topic = topic_in if topic_in else None
                else:
                    try:
                        topic_in = input(f"Enter topic for joke #{i+1} (leave blank for random): ").strip()
                    except EOFError:
                        topic_in = ""
                    topic = topic_in if topic_in else None

                print(f"Telling joke #{i+1} about: {topic or 'random'}")
                mgr.tell_joke(topic=topic, style="basic")
                time.sleep(1.0)
        else:
            mgr.expressive_say("Hello! Welcome to my show!", "happy")
            mgr.tell_joke(topic=None, style="basic")

    except KeyboardInterrupt:
        print("Demo interrupted by user")
    finally:
        print("Stopping OhBot and cleaning up...")
        mgr.stop()


if __name__ == "__main__":
    run_demo()
