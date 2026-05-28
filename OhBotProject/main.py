from ohbot import ohbot
from behavior.behavior_engine import BehaviorEngine


def main():
    robot = BehaviorEngine()

    try:
        ohbot.reset()
        robot.start()

        print("OhBot is ready.")
        print("Type something and press Enter.")
        print("Type 'exit' to stop.")

        while True:
            user_input = input("You: ")

            if user_input.lower() == "exit":
                break

            robot.respond(user_input)

    finally:
        robot.stop()
        ohbot.reset()
        ohbot.close()


if __name__ == "__main__":
    main()