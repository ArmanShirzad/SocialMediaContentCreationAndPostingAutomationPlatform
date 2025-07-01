# test_telegram_poster.py
import unittest
from unittest.mock import patch
from telegram_poster import TelegramPoster

class TestTelegramPoster(unittest.TestCase):
    def setUp(self):
        self.poster = TelegramPoster()

    @patch('telegram.Bot.send_message')
    @patch('telegram.Bot.send_photo')
    def test_post_to_channel(self, mock_send_photo, mock_send_message):
        title = "Test Title"
        url = "https://techcrunch.com/2024/10/19/four-takeaways-from-pony-ais-ipo-filing/"
        content = "This is a test message."
        image_url = None  # Provide a valid image URL if you want to test image posting

        # Call the method under test
        self.poster.post_to_channel(title=title, url=url, content=content, image_url=image_url)

        # Construct the expected message
        expected_message = f"*{title}*\n\n{content}\n\n[Read more]({url})"

        # Assert that send_message was called correctly
        mock_send_message.assert_called_once_with(
            chat_id=self.poster.chat_id,
            text=expected_message,
            parse_mode='MarkdownV2'
        )

        if image_url:
            mock_send_photo.assert_called_once_with(chat_id=self.poster.chat_id, photo=image_url)
        else:
            mock_send_photo.assert_not_called()

if __name__ == '__main__':
    unittest.main()
