import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
API_URL = os.getenv("AI_API_URL")
MODEL = os.getenv("AI_MODEL")


def ask_ai(prompt):

    if not API_KEY:
        return "AI API key is not configured."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are RecallAI, an intelligent learning "
                    "and memory assistant. Give concise, practical "
                    "study and revision recommendations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.4
    }

    try:

        response = requests.post(
            API_URL,
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as error:

        return f"AI service error: {error}"