"""Small runner that uses the behavior manager in OhBotProject.behavior."""

from OhBotProject.behavior.behavior_engine import OhBotBehaviorManager


if __name__ == "__main__":
    bot = OhBotBehaviorManager()

    try:
        bot.start()

        # Minimal interactive prompt preserved from original script
        print("\n=== OhBot Stand-up Comedian ===")
        print("1. Interactive Mode (you provide topics)")
        print("2. Automatic Mode (pre-set comedy routine)")

        try:
            choice = input("Choose mode (1 or 2): ").strip()
        except EOFError:
            choice = "2"

        if choice == "1":
            print("Interactive mode requires SpeechRecognition to be installed.")
            bot.expressive_say("Interactive mode requires speech recognition.", "sad")
        else:
            bot.expressive_say("Hello! Welcome to my show!", "happy")
            bot.tell_joke(topic=None, style="basic")

    except KeyboardInterrupt:
        print("\nStopping stand-up routine...")

    finally:
        bot.stop()
