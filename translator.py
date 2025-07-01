import os
import requests
import logging
import time

import logger

class GroqTranslator:
    def __init__(self, api_key=None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Error message patterns to check
        self.error_patterns = [
            "An unexpected error occurred",
            "Please try again later",
            "یک خطای غیرمنتظره رخ داد",
            "لطفاً بعداً دوباره تلاش کنید"
        ]

    def _validate_translation(self, translated_text):
        """Validate the translation doesn't contain error messages."""
        if not translated_text:
            return False
            
        for pattern in self.error_patterns:
            if pattern in translated_text:
                self.logger.error(f"Error pattern found in translation: {pattern}")
                return False
        return True

    def translate_to_persian(self, content, max_retries=3):
        """Translate with retry logic and validation."""
        self.logger.info("transaltion key" + self.api_key)

        if not content:
            self.logger.error("Empty content provided")
            return None

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; TechCrunchFarsiBot/1.0)'
        }

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": ("you are a professional english to persian translator."
                              '1- "Identify proper nouns (names of people, places, organizations, brands, etc.)."\n'
                              '2- "Do not translate proper nouns."\n'
                              '3- "Translate the given text to Persian."\n'
                              '4- "Ensure the translation is human-readable and makes sense in Persian."\n'
                              '5- "Align the text from right to left (RTL)."\n'
                              '6- "Unless for Proper Nouns, do not include any English words."\n'
                              '7- "Only provide the translated content."\n'
                              '8- "Format for Telegram compatibility with appropriate emojis."\n'
                              '9- "Maintain the original tone while being culturally relevant."\n')
                },  
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.1
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(self.endpoint, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()

                # Check for error messages before returning
                if any(error in translated_text for error in self.error_patterns):
                    self.logger.error("Error message detected in translation")
                    return None

                # Pass translated text to the proper nouns extractor
                # return self.extract_proper_nouns(translated_text)
                return translated_text

                
            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                return None
            
            # Wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        return None
    
    def extract_proper_nouns(self, content):
        if not content:
            self.logger.error("Empty content provided")
            return None

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; TechCrunchFarsiBot/1.0)'
        }

        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": ("you are a professional text editor.\n"
                                "1- 'Identify all proper nouns such as company names, person names, and specific named entities.'\n"
                                "2- 'if there's any proper nouns translated to persian make sure they are in English and the rest can stay persian (the translated language).'\n"
                                "3- 'Preserve the context and ensure emojis remain intact.'\n"
                                "4- 'Provide a final formatted response that maintains the text's original meaning and tone.'\n"
                                "5- 'Do not add explanations, only return the processed text.'")
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            processed_text = result['choices'][0]['message']['content'].strip()

            # Check for error messages before returning
            if any(error in processed_text for error in self.error_patterns):
                self.logger.error("Error message detected in processing")
                return None

            return processed_text

        except Exception as e:
            self.logger.error(f"Proper noun extraction error: {e}")
            return None

    def summarize_for_instagram(self, content, max_chars):
        """Summarize content to fit Instagram's character limit."""
        if not content or len(content) <= max_chars:
            return content

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; TechCrunchFarsiBot/1.0)'
        }

        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": ("You are a content summarizer specialized in maintaining key information while reducing text length.\n"
                              f"Summarize the following text to be under {max_chars} characters while:\n"
                              "1- Maintaining key information and proper nouns\n"
                              "2- Preserving the Persian language quality\n"
                              "3- Keeping essential emojis\n"
                              "4- Ensuring the summary is coherent and engaging"
                              "5- make sure your response do not include any english explaination and jus provide the final answer only."
                              )
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            summarized_text = result['choices'][0]['message']['content'].strip()
            
            if len(summarized_text) > max_chars:
                summarized_text = summarized_text[:max_chars-3] + "..."
                
            return summarized_text
            
        except Exception as e:
            self.logger.error(f"Summarization error: {e}")
            return None