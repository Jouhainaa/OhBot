import json
import os
from google import genai


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


SYSTEM_PROMPT = """
You are OhBot, a funny humanoid stand-up comedian robot.

You MUST respond ONLY with valid JSON.

Allowed moods:
neutral, happy, thrilled, angry, sad, surprise, sideeye

Allowed gestures:
nod, excited, sad_look, angry_look, surprised, sideeye, none

Rules:
- Be short.
- Be funny.
- Be suitable for a university demo.
- Do not write long paragraphs.
- Choose a mood that matches your answer.
- Choose one gesture.

Return exactly this format:
{
  "answer": "...",
  "mood": "...",
  "gesture": "..."
}
"""


def ask_chatgpt(user_input):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
{SYSTEM_PROMPT}

User says:
{user_input}
"""
        )

        text = response.text

        print("RAW GEMINI RESPONSE:")
        print(text)

        start = text.find("{")
        end = text.rfind("}") + 1
        json_text = text[start:end]

        data = json.loads(json_text)

        return {
            "answer": data.get("answer", "My comedy brain forgot the punchline."),
            "mood": data.get("mood", "neutral"),
            "gesture": data.get("gesture", "none")
        }

    except Exception as e:
        print("GEMINI ERROR:", e)

        return {
            "answer": "My AI brain has stage fright right now.",
            "mood": "sideeye",
            "gesture": "sideeye"
        }