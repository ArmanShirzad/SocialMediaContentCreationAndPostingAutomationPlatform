# test_workflow.py
import asyncio
from config import Config
from scraper import TechCrunchScraper
from translator import GroqTranslator
from telegram_poster import TelegramPoster
from instagram_poster import InstagramPoster
from llm_processor import LLMVideoAssistant
from database import ArticleDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_article():
    try:
        # Initialize components
        logger.info("1. Initializing components...")
        scraper = TechCrunchScraper()
        translator = GroqTranslator(Config.GROQ_API_KEY)
        telegram_poster = TelegramPoster()
        llm_assistant = LLMVideoAssistant(Config.GROQ_API_KEY)
        instagram_poster = InstagramPoster(translator, llm_assistant)
        db = ArticleDatabase()

        # 1. Scrape article
        logger.info("2. Scraping latest article...")
        articles = scraper.scrape_articles(limit=1)
        if not articles:
            raise Exception("No articles found")
        
        article_data = scraper.extract_article_data_v2(articles[0])
        
        # 2. Translate for Telegram
        logger.info("3. Translating content for Telegram...")
        telegram_title =  translator.translate_to_persian(article_data['title'])
        telegram_content =  translator.translate_to_persian(article_data['content'])
        
        # 3. Post to Telegram
        logger.info("4. Posting to Telegram...")
        telegram_message_ids = await telegram_poster.post_to_channel(
            telegram_title,
            telegram_content,
            article_data['image_url']
        )

        # 4. Process for Instagram/Video platforms
        logger.info("5. Processing for Instagram/Video...")
        
        # Summarize the content for Instagram
        instagram_caption = translator.summarize_for_instagram(telegram_content)
        
        # Generate keywords for video search
        keywords = llm_assistant.generate_keywords(article_data['title'] + " " + article_data['content'])
        logger.info(f"Generated keywords: {keywords}")

        # Choose video creation method
        use_stock_videos = True  # Toggle between videos/images
        
        if use_stock_videos:
            # Fetch one video per keyword
            logger.info("6a. Fetching stock videos...")
            video_assets = await instagram_poster.fetch_pexels_videos(
                keywords=keywords,
                videos_per_keyword=1  # Get one video per keyword
            )
            
            if video_assets:
                logger.info(f"Found {len(video_assets)} videos across {len(keywords)} keywords")
                # Create video with stock footage
                logger.info("7a. Creating video with stock footage...")
                video_path = await instagram_poster.create_video(
                    videos=video_assets,
                    content=article_data['title'] + " " + article_data['content']
                )
        else:
            # Fetch stock images from Pexels
            logger.info("6b. Fetching stock images...")
            image_assets = await instagram_poster.fetch_pexels_images(keywords)
            
            # Create video with images
            logger.info("7b. Creating video with images...")
            video_path = await instagram_poster.create_video_from_images(
                images=image_assets,
                content=instagram_caption
            )

        if video_path:
            # Queue for Instagram posting
            logger.info("8. Queueing for Instagram...")
            await instagram_poster.queue.add_to_queue(
                content=instagram_caption,
                media_path=video_path
            )
            
            # Update database
            db.update_posting_status(
                article_data['url'],
                telegram_ids=telegram_message_ids,
                instagram_posted=True
            )

        # Cleanup
        scraper.quit()
        logger.info("Workflow completed successfully")

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        if 'scraper' in locals():
            scraper.quit()

if __name__ == "__main__":
    asyncio.run(process_article())