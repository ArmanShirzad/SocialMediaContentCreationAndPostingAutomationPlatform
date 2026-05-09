import logging

from groq_client import GroqClient


class GroqTranslator:
    def __init__(self, api_key=None):
        self.logger = logging.getLogger(__name__)
        self.client = GroqClient(api_key)

        # Configure logging
        logging.basicConfig(level=logging.INFO)

    def translate_to_persian(self, content, max_retries=3):
        """Translate with retry logic and validation."""
        if not content:
            self.logger.error("Empty content provided")
            return None

        messages = [
            {
                "role": "system",
                "content": ("you are a professional english to korean translator."
                          '1- "Identify proper nouns (names of people, places, organizations, brands, etc.)."\n'
                          '2- "Do not translate proper nouns."\n'
                          '3- "Translate the given text to Korean."\n'
                          '4- "Ensure the translation is human-readable and makes sense in Korean."\n'
                          '5- "Do not include any English words unless they are proper nouns."\n'
                          '6- "Only provide the translated content."\n'
                          '7- "Format for Telegram compatibility with appropriate emojis."\n'
                          '8- "Maintain the original tone while being culturally relevant."\n')
            },
            {
                "role": "user",
                "content": content
            }
        ]

        return self.client.chat(messages, model="llama-3.3-70b-versatile",
                                temperature=0.1, max_retries=max_retries)
    
    def extract_proper_nouns(self, content):
        if not content:
            self.logger.error("Empty content provided")
            return None

        messages = [
            {
                "role": "system",
                "content": ("you are a professional text editor.\n"
                            "1- 'Identify all proper nouns such as company names, person names, and specific named entities.'\n"
                            "2- 'if there's any proper nouns translated to korean make sure they are in English and the rest can stay korean (the translated language).'\n"
                            "3- 'Preserve the context and ensure emojis remain intact.'\n"
                            "4- 'Provide a final formatted response that maintains the text's original meaning and tone.'\n"
                            "5- 'Do not add explanations, only return the processed text.'")
            },
            {
                "role": "user",
                "content": content
            }
        ]

        return self.client.chat(messages, model="llama-3.1-8b-instant")

    def summarize_for_instagram(self, content, max_chars):
        """Summarize content to fit Instagram's character limit."""
        if not content or len(content) <= max_chars:
            return content

        messages = [
            {
                "role": "system",
                "content": ("You are a content summarizer specialized in maintaining key information while reducing text length.\n"
                          f"Summarize the following text to be under {max_chars} characters while:\n"
                          "1- Maintaining key information and proper nouns\n"
                          "2- Preserving the Korean language quality\n"
                          "3- Keeping essential emojis\n"
                          "4- Ensuring the summary is coherent and engaging"
                          "5- make sure your response do not include any english explaination and jus provide the final answer only."
                          )
            },
            {
                "role": "user",
                "content": content
            }
        ]

        summarized_text = self.client.chat(
            messages, model="llama-3.3-70b-versatile", temperature=0.3
        )

        if summarized_text and len(summarized_text) > max_chars:
            summarized_text = summarized_text[:max_chars-3] + "..."

        return summarized_text