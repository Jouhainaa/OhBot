import time

from OhBotProject.behavior.behavior_engine import OhBotBehaviorManager


def run_demo():
    mgr = OhBotBehaviorManager()

    print("Starting OhBot behavior manager (blink loop active)...")
    mgr.start()

    try:
        # # 1) Blinking: let the blink loop run for a few seconds
        # print("Demo: blinking (watch the robot blink) for 4 seconds...")
        # time.sleep(5)
        #
        # # 2) Emotions: cycle through several moods
        # emotions = ["happy", "surprise", "sad", "angry"]
        # print("Demo: showing emotions")
        # for e in emotions:
        #     print(f" Setting mood: {e}")
        #     mgr.set_mood(e)
        #     time.sleep(5)
        #
        # # 3) Simple speaking: short expressive phrase
        # print("Demo: simple speaking")
        # mgr.expressive_say("Hello! I am OhBot. Nice to meet you.", mood="happy")
        # time.sleep(1)
        #
        # # 4) Comedian: tell a short joke (uses ComedyGenerator)
        # print("Demo: comedian — telling a short joke")
        # mgr.tell_joke()
        # time.sleep(1)

        # Minimal interactive prompt preserved from original script
        print("\n=== OhBot Stand-up Comedian ===")
        print("1. Interactive Mode (you provide topics)")
        print("2. Automatic Mode (pre-set comedy routine)")

        try:
            choice = input("Choose mode (1 or 2): ").strip()
        except EOFError:
            choice = "2"

        if choice == "1":
            num_jokes = 3
            try:
                num_input = input("How many jokes would you like? (default 3): ").strip()
                if num_input:
                    num_jokes = int(num_input)
            except (ValueError, EOFError):
                pass

            print("\nComedy Style:")
            print("  1 = Basic (short, punchy jokes)")
            print("  2 = Best (longer, sophisticated routines)")
            try:
                style_input = input("Choose style (1 or 2, default 1): ").strip()
                style = "best" if style_input == "2" else "basic"
            except EOFError:
                style = "basic"

            print(f"\nStarting {style} comedy session with {num_jokes} jokes...")
            print("(Make sure your microphone is ready!)\n")
            mgr.interactive_comedy_session(num_jokes=num_jokes, style=style)
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
