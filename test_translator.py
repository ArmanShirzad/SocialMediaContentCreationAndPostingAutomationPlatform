# test_translator.py
import unittest
import logging
from translator import GroqTranslator
from config import Config

class TestGroqTranslator(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.translator = GroqTranslator(api_key=Config.GROQ_API_KEY)
    
    def test_translate_to_persian(self):
        sample_text = "what the fuck?"
        translated_text = self.translator.translate_to_persian(sample_text)
        self.assertIsNotNone(translated_text, "Translation returned None")
        self.assertIsInstance(translated_text, str, "Translated text is not a string")
        print("Translated Text:", translated_text)
        # Optionally, check if the translated text is not equal to the input text
        self.assertNotEqual(translated_text, sample_text, "Translation did not occur")

if __name__ == '__main__':
    unittest.main()
