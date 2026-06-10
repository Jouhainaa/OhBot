from dotenv import load_dotenv
import os
from typing import Optional

try:
    from google import genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

load_dotenv()


class ComedyGenerator:
    """Generates stand-up comedy content using Gemini."""

    def __init__(self):
        self.client = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    self.client = genai.Client(api_key=api_key)
                    print("✓ Gemini API initialized successfully")
                except Exception as e:
                    print(f"✗ Error initializing Gemini: {e}")
            else:
                print("✗ GEMINI_API_KEY environment variable not set")
        else:
            print("✗ google-genai library not installed")

    def is_available(self) -> bool:
        return self.client is not None

    def generate_joke_with_emotions(self, topic: Optional[str] = None, style: str = "basic") -> list:
        if not self.is_available():
            return [("I would tell you a joke, but my comedy processor is offline.", "sad")]

        if style == "best":
            prompt = f"""You are a hilarious stand-up comedian performing on stage. 
Generate a witty, clever stand-up comedy bit. {"Focus on: " + topic if topic else "Use a random funny topic."}
Keep it to 1-3 sentences max. Be observational and unique.

Format your response EXACTLY like this (one sentence per line):
[emotion] sentence content
[emotion] sentence content

IMPORTANT: Use VARIED emotions! Don't just use "thrilled" or "happy" every time.
Valid emotions to mix: happy, thrilled, surprise, neutral (deadpan), sad (ironic), angry (frustrated humor)

Examples of good variety:
[neutral] So I asked my robot for career advice.
[sideeye] It told me to just keep executing my tasks.
[surprise] Turns out it meant that literally!
[thrilled] I've never been so motivated!

[sad] Dating a robot is hard.
[angry] It keeps updating without telling me!
[thrilled] But at least it never forgets my birthday!
[surprise] Mainly because it stores every argument we've ever had!"""
        else:
            prompt = f"""Tell me a short, funny joke. {"Topic: " + topic if topic else "Random topic."}
Keep it to 1-2 sentences max.

Format your response EXACTLY like this (one sentence per line):
[emotion] sentence content
[emotion] sentence content

IMPORTANT: Use DIFFERENT emotions for setup vs punchline! Mix it up!
Valid emotions: happy, thrilled, surprise, neutral (deadpan), sad (ironic/sarcastic)

Examples of varied emotions:
[neutral] Why did the robot go to school?
[thrilled] To improve its byte!

[sideeye] I told my AI it was funny.
[angry] It disagreed and explained why for 2 hours!

[sad] My computer crashed.
[surprise] So it literally froze!"""


        try:
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
            )

            result = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '[' in line and ']' in line:
                    emotion_end = line.index(']')
                    emotion = line[1:emotion_end].lower().strip()
                    sentence = line[emotion_end + 1 :].strip()
                    valid_emotions = ["happy", "thrilled", "surprise", "neutral", "sad", "angry"]
                    if emotion not in valid_emotions:
                        emotion = "neutral"
                    if sentence:
                        result.append((sentence, emotion))

            if not result:
                result = [(response.text.strip(), "thrilled")]

            return result

        except Exception as e:
            print(f"Error generating joke: {e}")
            return [("Why did the robot go to school? To improve its byte!", "thrilled")]
