# telegram_poster.py
import asyncio
import logging
from telegram import Bot
from config import Config
from datetime import datetime

class TelegramPoster:
    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.chat_id = Config.TELEGRAM_CHAT_ID
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        self.error_patterns = [
            "An unexpected error occurred",
            "Please try again later",
            "یک خطای غیرمنتظره رخ داد",
            "لطفاً بعداً دوباره تلاش کنید"
        ]

        self.MAX_CAPTION_LENGTH = 1024  # Telegram's limit for photo captions
        self.MAX_MESSAGE_LENGTH = 4096  # Telegram's limit for text messages

    def _log_content(self, stage, **content):
        """Log content at various stages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('logs/detailed_flow.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Stage: {stage}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"{'='*50}\n")
            for key, value in content.items():
                f.write(f"\n{key}:\n{'-'*50}\n{value}\n{'-'*50}\n")

    async def post_to_channel(self, title, content, image_url=None):
        self.logger.info(f"Starting post to channel with image_url: {image_url}")
        
        try:
            message_ids = []
            
            # If we have an image, send it with a caption containing the title and first part of content
            if image_url:
                caption = f"{title}\n\n{content[:self.MAX_CAPTION_LENGTH-len(title)-4]}"
                photo_message = await self._send_photo_with_retry(image_url, caption)
                if photo_message:
                    message_ids.append(photo_message.message_id)
                    # Remove the part we already sent in the caption
                    content = content[self.MAX_CAPTION_LENGTH-len(title)-4:]

            # Send remaining content in chunks if necessary
            while content:
                chunk = content[:self.MAX_MESSAGE_LENGTH]
                content = content[self.MAX_MESSAGE_LENGTH:]
                
                message = await self._send_message_with_retry(chunk)
                if message:
                    message_ids.append(message.message_id)

            return message_ids if message_ids else None

        except Exception as e:
            self.logger.error(f"Error in post_to_channel: {e}")
            return None

    async def _send_message_with_retry(self, text, retries=3):
        for i in range(retries):
            try:
                return await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode='HTML'  # Changed from Markdown to HTML for better compatibility
                )
            except Exception as e:
                self.logger.error(f"Error sending message (attempt {i+1}/{retries}): {e}")
                if i == retries - 1:
                    raise
                await asyncio.sleep(2)

    async def _send_photo_with_retry(self, image_url, caption, retries=3):
        for i in range(retries):
            try:
                return await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=image_url,
                    caption=caption,
                    parse_mode='HTML'  # Changed from Markdown to HTML for better compatibility
                )
            except Exception as e:
                self.logger.error(f"Error sending photo (attempt {i+1}/{retries}): {e}")
                if i == retries - 1:
                    raise
                await asyncio.sleep(2)

    def _escape_markdown(self, text):
        """Escape special characters for MarkdownV2"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        escaped_text = text
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        return escaped_text
