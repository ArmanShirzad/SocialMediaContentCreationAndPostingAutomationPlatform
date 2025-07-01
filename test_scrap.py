

#region
# from telethon import TelegramClient
# from config import Config
# import asyncio

# api_id = Config.TELEGRAM_API_ID
# api_hash = Config.TELEGRAM_API_HASH

# client = TelegramClient('anon', api_id, api_hash)

# async def send_message():
#     await client.start()
#     try:
#         # Use a random image from the internet
#         image_url = 'https://via.placeholder.com/1024x683.png'  # Random placeholder image URL
#         caption = "This is a test message with a random image!"  # Caption

#         # Send the image with the caption as the message
#         await client.send_file(Config.TELEGRAM_CHAT_ID, image_url, caption=caption)
#         print("Message with image sent successfully!")
#     except Exception as e:
#         print(f"Error posting to Telegram: {e}")

#     await client.disconnect()

# if __name__ == '__main__':
#     asyncio.run(send_message())


#endregion

import asyncio
from telegram import Bot
from config import Config

async def post_to_telegram():
    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    try:
        # Use a random image from the internet
        image_url = 'https://via.placeholder.com/1024x683.png'  # Random placeholder image URL
        caption = "This is a test message with a random image!"  # Caption

        # Send the image with the caption as the message
        await bot.send_photo(chat_id=Config.TELEGRAM_CHAT_ID, photo=image_url, caption=caption)
        print("Message with image posted successfully!")
    except Exception as e:
        print(f"Error posting to Telegram: {e}")

if __name__ == '__main__':
    asyncio.run(post_to_telegram())

#     asyncio.run(post_to_telegram())
