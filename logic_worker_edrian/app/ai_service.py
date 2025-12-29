import os
import logging
import requests

log = logging.getLogger("ai_service")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class AIService:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")

        if not self.api_key:
            log.warning(
                "DEEPSEEK_API_KEY not set - AI service will return mock responses"
            )

    def generate_response(self, user_text: str) -> str:
        log.info("Generating AI response")

        if not user_text or not user_text.strip():
            return (
                "I received an empty message. "
                "Please provide a question or request so I can help you."
            )

        # Mock mode (no API key)
        if not self.api_key:
            return (
                f"[MOCK RESPONSE]\n"
                f"You asked: '{user_text.strip()}'\n"
                f"This is a simulated response because DEEPSEEK_API_KEY is not configured."
            )

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Provide clear, concise, and accurate answers."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text.strip(),
                },
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                json=payload,
                headers=headers,
                timeout=60,
            )

            response.raise_for_status()
            data = response.json()

            result = data["choices"][0]["message"]["content"]
            log.info("AI response generated successfully")
            return result

        except requests.exceptions.RequestException as e:
            log.error(f"DeepSeek API request failed: {e}")
            return (
                "I'm sorry, I encountered an error while contacting the AI service. "
                "Please try again later."
            )
        except (KeyError, IndexError) as e:
            log.error(f"Unexpected DeepSeek response format: {e}")
            return (
                "I received an unexpected response format from the AI service."
            )
