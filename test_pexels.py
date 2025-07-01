# test_pexels.py
import asyncio
from instagram_poster import InstagramPoster
from translator import GroqTranslator
from config import Config
import logging

logging.basicConfig(level=logging.INFO)

async def test_pexels_api():
    translator = GroqTranslator(Config.GROQ_API_KEY)
    poster = InstagramPoster(translator)
    
    # Test with some keywords
    keywords = ["technology", "innovation", "future"]
    videos = await poster.fetch_pexels_videos(keywords, limit=3)
    
    if videos:
        print(f"Successfully fetched {len(videos)} videos")
        for video in videos:
            print(f"Video ID: {video['id']}, Duration: {video['duration']}s")
            print(f"URL: {video['url']}")
            print("-" * 50)
    else:
        print("No videos found or error occurred")

if __name__ == "__main__":
    asyncio.run(test_pexels_api())