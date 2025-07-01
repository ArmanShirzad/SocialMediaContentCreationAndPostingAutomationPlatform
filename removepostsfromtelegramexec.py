# delete_messages.py
import asyncio
from telegram import Bot
from config import Config
from database import ArticleDatabase

async def delete_messages(limit=None, specific_message_id=None):
    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    chat_id = Config.TELEGRAM_CHAT_ID
    db = ArticleDatabase()

    try:
        # Retrieve articles with message_ids
        query = "SELECT url, message_ids FROM articles WHERE message_ids IS NOT NULL"
        articles = db.conn.execute(query).fetchall()

        deleted_count = 0
        for article in articles:
            url, message_ids_str = article
            if not message_ids_str:
                continue

            message_ids = list(map(int, message_ids_str.split(',')))

            for message_id in message_ids:
                # Check if we should stop after reaching the limit
                if limit is not None and deleted_count >= limit:
                    print(f"Deleted {deleted_count} messages as requested.")
                    return

                # Check if we are deleting only a specific message ID
                if specific_message_id is not None and message_id != specific_message_id:
                    continue

                try:
                    await bot.delete_message(chat_id=chat_id, message_id=message_id)
                    print(f"Deleted message {message_id}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete message {message_id}: {e}")

            # Optionally, remove message_ids from the database after deletion if all messages are deleted
            db.conn.execute("UPDATE articles SET message_ids = NULL WHERE url = ?", (url,))
            db.conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

# Usage example
if __name__ == "__main__":
    asyncio.run(delete_messages(limit=10))  # Example: delete the 10 most recent messages
    # asyncio.run(delete_messages(specific_message_id=123456))  # Example: delete a specific message ID

