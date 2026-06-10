import os
from typing import Optional

try:
    from google import genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False


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
            prompt = """You are a hilarious stand-up comedian performing on stage. Keep it to 1-3 sentences max.
Format your response EXACTLY like this (one sentence per line):
[emotion] sentence content
"""
        else:
            prompt = """Tell me a short, funny joke. Keep it to 1-2 sentences max.
Format your response EXACTLY like this (one sentence per line):
[emotion] sentence content
"""

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
                    valid_emotions = ["happy", "thrilled", "surprise", "sideeye", "neutral", "sad", "angry"]
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
