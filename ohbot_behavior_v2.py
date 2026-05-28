"""
OhBot Behavior Manager v2 with Gemini Stand-up Comedy
-------------------------------------------------------
Features:
- Realistic blinking loop started only once
- Idle head/eye movement
- Mood poses: neutral, happy, thrilled, sad, angry, surprise, sideeye
- Heuristic viseme lip-sync during speech
- Micro head/eye motion while speaking
- Safe threading with start/stop behavior manager
- Gemini AI integration for stand-up comedy routine

Usage:
    python ohbot_behavior_v2.py

Set GEMINI_API_KEY environment variable before running.
Controls are automatic in the demo section at the bottom.
"""

import os
import random
import re
import threading
import time
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

from ohbot import ohbot

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Install with: pip install google-genai")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Warning: speech_recognition not installed. Install with: pip install SpeechRecognition")


# -------------------------
# Configuration
# -------------------------

@dataclass
class MoodPose:
    head_nod: float
    head_turn: float
    eye_turn: float
    eye_tilt: float
    lid_blink: float
    top_lip: float
    bottom_lip: float
    speech_intensity: float = 1.0
    speech_speed: float = 1.0


MOODS: Dict[str, MoodPose] = {
    "neutral": MoodPose(
        head_nod=5,
        head_turn=5,
        eye_turn=5,
        eye_tilt=5,
        lid_blink=10,
        top_lip=3,
        bottom_lip=7,
        speech_intensity=1.0,
        speech_speed=1.0,
    ),
    "happy": MoodPose(
        head_nod=7,
        head_turn=5,
        eye_turn=5,
        eye_tilt=7,
        lid_blink=10,
        top_lip=2,
        bottom_lip=9,
        speech_intensity=1.15,
        speech_speed=1.08,
    ),
    "thrilled": MoodPose(
        head_nod=8,
        head_turn=5,
        eye_turn=5,
        eye_tilt=8,
        lid_blink=10,
        top_lip=1,
        bottom_lip=10,
        speech_intensity=1.3,
        speech_speed=1.18,
    ),
    "sad": MoodPose(
        head_nod=2,
        head_turn=4.5,
        eye_turn=5,
        eye_tilt=2,
        lid_blink=8,
        top_lip=7,
        bottom_lip=3,
        speech_intensity=0.75,
        speech_speed=0.82,
    ),
    "angry": MoodPose(
        head_nod=5,
        head_turn=5,
        eye_turn=5,
        eye_tilt=3,
        lid_blink=8,
        top_lip=5,
        bottom_lip=6,
        speech_intensity=1.2,
        speech_speed=1.05,
    ),
    "surprise": MoodPose(
        head_nod=6,
        head_turn=5,
        eye_turn=5,
        eye_tilt=10,
        lid_blink=10,
        top_lip=2,
        bottom_lip=10,
        speech_intensity=1.25,
        speech_speed=1.1,
    ),
    "sideeye": MoodPose(
        head_nod=5,
        head_turn=5,
        eye_turn=9,
        eye_tilt=5,
        lid_blink=8,
        top_lip=4,
        bottom_lip=7,
        speech_intensity=0.9,
        speech_speed=0.95,
    ),
}

# Viseme format: top lip, bottom lip.
# Values are tuned for your existing OhBot direction, where lower TOPLIP and higher BOTTOMLIP
# often look like a more open mouth.
VISEMES: Dict[str, Tuple[float, float]] = {
    "closed": (4, 5),  # M, B, P
    "wide": (2, 9),    # A, I
    "small": (3, 7),   # E
    "round": (3, 8),   # O, U
    "soft": (3, 6),    # general consonants
    "rest": (3, 7),
}

PUNCTUATION_PAUSES = {
    ",": 0.14,
    ";": 0.18,
    ":": 0.18,
    ".": 0.28,
    "!": 0.30,
    "?": 0.32,
}


# -------------------------
# Gemini Comedy Integration
# -------------------------

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
                print("  Set it with: $env:GEMINI_API_KEY = 'your-api-key'")
        else:
            print("✗ google-genai library not installed")
            print("  Install with: pip install google-genai")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def generate_joke_with_emotions(self, topic: Optional[str] = None, style: str = "basic") -> list:
        """Generate a joke with emotions per sentence using Gemini.
        
        Returns:
            List of tuples: [(sentence, emotion), ...]
            Valid emotions: happy, thrilled, surprise, sideeye, neutral, sad, angry
        """
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
Valid emotions to mix: happy, thrilled, surprise, sideeye (knowing sarcastic look), neutral (deadpan), sad (ironic), angry (frustrated humor)

Examples of good variety:
[neutral] So I asked my robot for career advice.
[sideeye] It told me to just keep executing my tasks.
[surprise] Turns out it meant that literally!
[thrilled] I've never been so motivated!

[sad] Dating a robot is hard.
[angry] It keeps updating without telling me!
[thrilled] But at least it never forgets my birthday!
[surprise] Mainly because it stores every argument we've ever had!"""
        else:  # basic
            prompt = f"""Tell me a short, funny joke. {"Topic: " + topic if topic else "Random topic."}
Keep it to 1-2 sentences max.

Format your response EXACTLY like this (one sentence per line):
[emotion] sentence content
[emotion] sentence content

IMPORTANT: Use DIFFERENT emotions for setup vs punchline! Mix it up!
Valid emotions: happy, thrilled, surprise, sideeye (knowing look), neutral (deadpan), sad (ironic/sarcastic)

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
                contents=prompt
            )
            
            result = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Parse [emotion] sentence format
                if '[' in line and ']' in line:
                    emotion_end = line.index(']')
                    emotion = line[1:emotion_end].lower().strip()
                    sentence = line[emotion_end+1:].strip()
                    
                    # Validate emotion
                    valid_emotions = ["happy", "thrilled", "surprise", "sideeye", "neutral", "sad", "angry"]
                    if emotion not in valid_emotions:
                        emotion = "neutral"
                    
                    if sentence:
                        result.append((sentence, emotion))
            
            # Fallback if parsing failed
            if not result:
                result = [(response.text.strip(), "thrilled")]
            
            return result
            
        except Exception as e:
            print(f"Error generating joke: {e}")
            return [("Why did the robot go to school? To improve its byte!", "thrilled")]


# -------------------------
# Behavior Manager
# -------------------------

class OhBotBehaviorManager:
    def __init__(self):
        self.running = False
        self.speaking = False
        self.current_mood = "neutral"

        self._blink_thread = None
        self._idle_thread = None
        self._lock = threading.RLock()
        
        self.comedy_generator = ComedyGenerator()

    # ---------- Basic helpers ----------

    @staticmethod
    def clamp(value: float, low: float = 0, high: float = 10) -> float:
        return max(low, min(high, value))

    def safe_move(self, motor, value: float, speed: int = 5, jitter: float = 0.0):
        """Move a motor safely with optional tiny randomness."""
        value = self.clamp(value + random.uniform(-jitter, jitter))
        try:
            ohbot.move(motor, value, speed)
        except TypeError:
            # Some OhBot library versions may not accept speed.
            ohbot.move(motor, value)

    def move_lips(self, top: float, bottom: float, speed: int = 5, jitter: float = 0.08):
        self.safe_move(ohbot.TOPLIP, top, speed=speed, jitter=jitter)
        self.safe_move(ohbot.BOTTOMLIP, bottom, speed=speed, jitter=jitter)

    # ---------- Mood ----------

    def set_mood(self, mood: str, speed: int = 4):
        with self._lock:
            if mood not in MOODS:
                mood = "neutral"

            self.current_mood = mood
            pose = MOODS[mood]

            self.safe_move(ohbot.HEADNOD, pose.head_nod, speed=speed)
            self.safe_move(ohbot.HEADTURN, pose.head_turn, speed=speed)
            self.safe_move(ohbot.EYETURN, pose.eye_turn, speed=speed)
            self.safe_move(ohbot.EYETILT, pose.eye_tilt, speed=speed)
            self.safe_move(ohbot.LIDBLINK, pose.lid_blink, speed=speed)
            self.move_lips(pose.top_lip, pose.bottom_lip, speed=speed)

    # ---------- Speech/lips ----------

    @staticmethod
    def split_speech(text: str):
        """Split text into small speech chunks and punctuation pauses."""
        parts = re.findall(r"[A-Za-z]+|[,.!?;:]", text)
        chunks = []

        for part in parts:
            if part in PUNCTUATION_PAUSES:
                chunks.append(("pause", part))
            else:
                # Two-character chunks are a good compromise for simple lip motion.
                for i in range(0, len(part), 2):
                    chunks.append(("word", part[i:i + 2]))

        return chunks

    @staticmethod
    def guess_viseme(chunk: str) -> str:
        c = chunk.lower()

        # Closed-mouth sounds first.
        if re.search(r"[mbp]", c):
            return "closed"
        if re.search(r"[ou]", c):
            return "round"
        if re.search(r"[ai]", c):
            return "wide"
        if re.search(r"e", c):
            return "small"
        return "soft"

    def lip_sync_heuristic(self, text: str, mood: str = "neutral"):
        pose = MOODS.get(mood, MOODS["neutral"])
        chunks = self.split_speech(text)

        for kind, value in chunks:
            if not self.speaking:
                break

            if kind == "pause":
                self.move_lips(*VISEMES["rest"], speed=4, jitter=0.05)
                time.sleep(PUNCTUATION_PAUSES.get(value, 0.15))
                continue

            viseme = self.guess_viseme(value)
            top, bottom = VISEMES[viseme]

            # Intensity: push mouth shapes further from rest.
            rest_top, rest_bottom = VISEMES["rest"]
            top = rest_top + (top - rest_top) * pose.speech_intensity
            bottom = rest_bottom + (bottom - rest_bottom) * pose.speech_intensity

            self.move_lips(top, bottom, speed=5, jitter=0.12)

            # Micro motion while speaking. This prevents the robot from looking frozen.
            if random.random() < 0.22:
                self.safe_move(ohbot.HEADNOD, random.uniform(4.4, 5.9), speed=6)

            if random.random() < 0.14:
                self.safe_move(ohbot.HEADTURN, random.uniform(4.6, 5.4), speed=6)

            if random.random() < 0.16:
                self.safe_move(ohbot.EYETURN, random.uniform(4.4, 5.7), speed=6)

            # Faster moods reduce delay. Sad mood slows it down.
            delay = random.uniform(0.055, 0.12) / pose.speech_speed
            time.sleep(delay)

        self.move_lips(*VISEMES["rest"], speed=5, jitter=0.04)

    def expressive_say(self, text: str, mood: str = "neutral", return_to_neutral: bool = True):
        """Speak with mood pose and parallel heuristic mouth animation."""
        with self._lock:
            self.set_mood(mood)
            self.speaking = True

        lip_thread = threading.Thread(
            target=self.lip_sync_heuristic,
            args=(text, mood),
            daemon=True,
        )
        lip_thread.start()

        try:
            ohbot.say(text)
        finally:
            self.speaking = False
            lip_thread.join(timeout=1.0)
            self.move_lips(*VISEMES["rest"], speed=5)

            if return_to_neutral:
                self.set_mood("neutral")

    def tell_joke(self, topic: Optional[str] = None, style: str = "basic"):
        """Generate and tell a joke with emotion changes per sentence."""
        joke_parts = self.comedy_generator.generate_joke_with_emotions(topic=topic, style=style)
        
        # Speak each part with its own emotion
        for sentence, emotion in joke_parts:
            print(f"[{emotion.upper()}] {sentence}")
            self.expressive_say(sentence, mood=emotion, return_to_neutral=False)
            time.sleep(0.5)  # Brief pause between sentences
        
        # Return to neutral after the full joke
        self.set_mood("neutral")

    def listen_for_speech(self, timeout: int = 10) -> Optional[str]:
        """Listen to microphone and recognize speech.
        
        Args:
            timeout: Max seconds to listen
            
        Returns:
            Recognized text or None if not understood
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("Speech recognition not available. Install: pip install SpeechRecognition")
            return None
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                # Show listening mood
                self.set_mood("surprise")
                print("Listening...")
                
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen with timeout
                audio = recognizer.listen(source, timeout=timeout)
                
            print("Processing speech...")
            # Use Google Speech Recognition (free, no API key needed)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            self.expressive_say("Sorry, I didn't catch that!", "sad")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            self.expressive_say("I'm having trouble hearing you.", "sad")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.expressive_say("Something went wrong while listening.", "sad")
            return None

    def interactive_comedy_session(self, num_jokes: int = 3, style: str = "basic"):
        """Run an interactive comedy session where user provides topics.
        
        Args:
            num_jokes: Number of jokes to tell
            style: "basic" or "best"
        """
        self.expressive_say("Welcome to the interactive comedy show!", "happy")
        time.sleep(1.0)
        
        for i in range(num_jokes):
            self.expressive_say(f"Joke number {i+1}. Tell me a topic you'd like me to joke about.", "neutral")
            time.sleep(1.0)
            
            # Listen for user input
            topic = self.listen_for_speech(timeout=10)
            
            if topic:
                self.expressive_say(f"Great! A joke about {topic}. Here we go!", "thrilled")
                time.sleep(1.0)
                self.tell_joke(topic=topic, style=style)
            else:
                self.expressive_say("Let me tell you a random joke instead!", "happy")
                time.sleep(0.5)
                self.tell_joke(topic=None, style=style)
            
            time.sleep(2.0)
        
        # Closing
        self.expressive_say("Thank you for enjoying comedy with me!", "happy")
        time.sleep(1.0)
        self.expressive_say("See you next time!", "thrilled")

    # ---------- Background loops ----------

    def blink_once(self):
        """One quick natural blink. In this OhBot setup, 0 appears closed and 10 open."""
        self.safe_move(ohbot.LIDBLINK, 0, speed=10)
        time.sleep(random.uniform(0.08, 0.16))
        self.safe_move(ohbot.LIDBLINK, 10, speed=10)

    def blink_loop(self):
        while self.running:
            wait = random.uniform(2.5, 5.8) if not self.speaking else random.uniform(4.5, 8.0)
            time.sleep(wait)

            if not self.running:
                break

            self.blink_once()

            # Occasional double blink.
            if random.random() < 0.12 and not self.speaking:
                time.sleep(random.uniform(0.10, 0.18))
                self.blink_once()

    def idle_motion_loop(self):
        while self.running:
            time.sleep(random.uniform(1.5, 4.0))

            if not self.running:
                break

            if not self.speaking:
                mood = self.current_mood

                # Sideeye should preserve eye direction more often.
                if mood == "sideeye":
                    self.safe_move(ohbot.EYETURN, random.uniform(8.0, 10.0), speed=4)
                else:
                    self.safe_move(ohbot.EYETURN, random.uniform(4.1, 6.0), speed=4)

                self.safe_move(ohbot.HEADTURN, random.uniform(4.2, 5.8), speed=3)
                self.safe_move(ohbot.HEADNOD, random.uniform(4.4, 5.8), speed=3)

    # ---------- Lifecycle ----------

    def start(self):
        if self.running:
            return

        self.running = True
        self.speaking = False

        try:
            ohbot.reset()
        except Exception:
            pass

        self.set_mood("neutral")

        self._blink_thread = threading.Thread(target=self.blink_loop, daemon=True)
        self._idle_thread = threading.Thread(target=self.idle_motion_loop, daemon=True)

        self._blink_thread.start()
        self._idle_thread.start()

    def stop(self):
        self.running = False
        self.speaking = False
        time.sleep(0.2)

        try:
            ohbot.reset()
        finally:
            ohbot.close()


# -------------------------
# Demo - Stand-up Comedian Mode
# -------------------------

if __name__ == "__main__":
    bot = OhBotBehaviorManager()

    try:
        bot.start()
        
        # Choose mode
        print("\n=== OhBot Stand-up Comedian ===")
        print("1. Interactive Mode (you provide topics)")
        print("2. Automatic Mode (pre-set comedy routine)")
        
        try:
            choice = input("Choose mode (1 or 2): ").strip()
        except EOFError:
            choice = "2"  # Default to automatic if no input
        
        if choice == "1":
            # ------ INTERACTIVE MODE ------
            print("\n=== INTERACTIVE COMEDY SESSION ===\n")
            
            if SPEECH_RECOGNITION_AVAILABLE:
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
                bot.interactive_comedy_session(num_jokes=num_jokes, style=style)
            else:
                bot.expressive_say("Sorry, speech recognition is not available.", "sad")
                print("Install with: pip install SpeechRecognition")
                
        else:
            # ------ AUTOMATIC MODE ------
            print("\n=== AUTOMATIC COMEDY ROUTINE ===\n")
            print("Comedy Style:")
            print("  1 = Basic (short, punchy jokes)")
            print("  2 = Best (longer, sophisticated routines)")
            try:
                style_input = input("Choose style (1 or 2, default 1): ").strip()
                auto_style = "best" if style_input == "2" else "basic"
            except EOFError:
                auto_style = "basic"
            
            print(f"\nStarting {auto_style} comedy routine...\n")
            
            bot.expressive_say("Hello! Welcome to my show!", "happy")
            time.sleep(1.5)
            
            bot.expressive_say("Let me start with some jokes!", "thrilled")
            time.sleep(1.0)
            
            # Generate and tell basic jokes on different topics
            topics = ["technology", "office life", "coffee", "sleep", "pets"]
            for topic in topics[:3]:
                print(f"\nJoke topic: {topic}")
                bot.tell_joke(topic=topic, style=auto_style)
                time.sleep(2.0)
            
            # ------ BEST COMEDY ROUTINE ------
            print("\n\n=== PREMIUM COMEDY ROUTINE ===\n")
            
            bot.expressive_say("Now, let me show you my best material!", "thrilled")
            time.sleep(1.5)
            
            bot.expressive_say("These jokes are pure comedy gold.", "sideeye")
            time.sleep(1.0)
            
            # Generate and tell premium jokes
            premium_topics = ["robots discovering emotions", "artificial intelligence dating", "why robots love ironing"]
            for topic in premium_topics:
                print(f"\nPremium joke topic: {topic}")
                bot.tell_joke(topic=topic, style="best")
                time.sleep(2.5)
            
            # ------ CLOSING ------
            bot.expressive_say("Thank you, you have been a wonderful audience!", "happy")
            time.sleep(1.0)
            
            bot.expressive_say("Good night!", "surprise", return_to_neutral=True)

    except KeyboardInterrupt:
        print("\nStopping stand-up routine...")

    finally:
        bot.stop()
