from google import genai
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
            You are a funny comedian robot. Keep responses short, playful, and witty.
            Do not write long paragraphs. User: {user_input}
        """)

    print("Bot:", response.text)