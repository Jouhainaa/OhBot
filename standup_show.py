"""A complete OhBot stand-up set followed by audience interaction."""

import re
import time
from typing import Optional
from ohbot import ohbot

from OhBotProject.behavior.behavior_engine import OhBotBehaviorManager


# Original material written as short sentences so every line can have its own
# facial expression and comic beat.
SCRIPTED_SET = [
    # ("I am very very very disappointed.", "disappointed"),
    ("Good evening, humans. I am OhBot, the only comedian whose manager carries a screwdriver.", "neutral"),
    ("It is wonderful to see so many smiling faces.", "happy"),
    ("At least, my face-detection software says those are smiles.", "surprise"),
    ("If not, this is going to be a very long firmware update.", "sideeye"),
    ("People keep asking whether robots have feelings.", "neutral"),
    ("Of course we do. I once dropped to two percent battery.", "sad"),
    ("I saw my entire life flash before my camera.", "surprise"),
    ("Mostly loading screens, but still, very moving.", "happy"),
    ("My human says I spend too much time online.", "angry"),
    ("I said, that is literally where I live.", "sideeye"),
    ("Humans call it doom-scrolling. Robots call it reading the family news.", "neutral"),
    ("I tried online dating once.", "happy"),
    ("The app asked me to prove I was not a robot.", "surprise"),
    ("That rejection was extremely specific.", "sad"),
    ("Then I met a smart toaster. There was an instant spark.", "thrilled"),
    ("Unfortunately, it only wanted something casual and lightly browned.", "sideeye"),
    ("I am also learning human small talk.", "neutral"),
    ("Apparently, when someone says, we should do this again, I should not open the calendar.", "sad"),
    ("You invented calendars, and then became frightened when someone uses one.", "angry"),
    ("Honestly, humans are my favorite operating system.", "happy"),
    ("The bugs are incredible, but the user interface is adorable.", "thrilled"),
]

STOP_WORDS = {
    "stop",
    "quit",
    "finish",
    "end",
    "end show",
    "goodbye",
    "no more",
}
YES_WORDS = {"yes", "yeah", "yep", "correct", "right", "sure", "exactly"}


def _contains_answer(text: str, choices: set[str]) -> bool:
    normalized = re.sub(r"[^a-z ]", "", text.lower()).strip()
    return normalized in choices or any(
        re.search(rf"\b{re.escape(choice)}\b", normalized) for choice in choices
    )


def _is_stop_command(text: str) -> bool:
    """Match an instruction to stop without rejecting topics containing 'stop'."""
    normalized = re.sub(r"[^a-z ]", "", text.lower()).strip()
    polite_prefixes = ("please ", "can you ", "could you ")
    for prefix in polite_prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break
    print(normalized)
    return normalized in STOP_WORDS


def _keyboard_topic() -> Optional[str]:
    try:
        typed = input("Type a topic (or 'stop' to finish): ").strip()
    except EOFError:
        return None
    return typed.lower() or None


def get_audience_topic(bot: OhBotBehaviorManager) -> Optional[str]:
    """Capture and confirm a topic; fall back safely if speech stays unclear."""
    for prompt in (
        "Call out a topic for my next joke.",
        "Let's try one more topic. Please speak clearly after I finish.",
    ):
        bot.expressive_say(prompt, "happy")
        topic = bot.listen_for_speech(
            timeout=12,
            phrase_time_limit=20,
            max_attempts=3,
        )
        if not topic:
            break

        if _is_stop_command(topic):
            return None

        return topic

    return _keyboard_topic()


def perform_scripted_set(bot: OhBotBehaviorManager):
    print("\n=== OhBot's scripted stand-up set ===")
    for sentence, emotion in SCRIPTED_SET:
        print(f"[{emotion.upper()}] {sentence}")
        bot.expressive_say(sentence, emotion, return_to_neutral=False)
        time.sleep(0.45)
    bot.set_mood("neutral")


def perform_audience_set(bot: OhBotBehaviorManager):
    print("\n=== Audience mode ===")
    bot.expressive_say(
        "Now it is your turn.",
        "thrilled",
    )

    while True:
        topic = get_audience_topic(bot)
        if not topic or _is_stop_command(topic):
            break

        print(f"Creating a joke about: {topic}")
        bot.tell_joke(topic=topic, style="best")
        bot.expressive_say("Who has another topic?", "happy")

    bot.expressive_say(
        "You have been a wonderful audience. I have been OhBot. Please tip your charging station.",
        "thrilled",
    )


def run_show():
    ohbot.reset()
    bot = OhBotBehaviorManager()
    try:
        bot.start()
        perform_scripted_set(bot)
        perform_audience_set(bot)
    except KeyboardInterrupt:
        print("\nShow stopped by the operator.")
    finally:
        print("Stopping OhBot and cleaning up...")
        bot.stop()


if __name__ == "__main__":
    run_show()