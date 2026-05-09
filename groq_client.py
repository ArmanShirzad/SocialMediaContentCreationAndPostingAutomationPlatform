import os
import logging
import time
import requests
from typing import Optional

logger = logging.getLogger(__name__)

ERROR_PATTERNS = [
    "An unexpected error occurred",
    "Please try again later",
]


class GroqClient:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")

    def chat(self, messages: list, model: str = "llama-3.3-70b-versatile",
             temperature: float = 0.1, max_retries: int = 3) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(self.API_URL, headers=headers, json=data)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"].strip()

                if any(p in content for p in ERROR_PATTERNS):
                    logger.error("Error pattern detected in Groq response")
                    return None

                return content
            except Exception as e:
                logger.error(f"Groq API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        return None
