# main_no_instagram.py
import asyncio
from scraper import TechCrunchScraper
from telegram_poster import TelegramPoster
from test_x_posting import XPoster
from translator import GroqTranslator
# from chatgptTranslator import ChatGPTTranslator
from database import ArticleDatabase
from logger import log_to_file
import os
import aiohttp
import time
from typing import Optional
from llm_processor import LLMVideoAssistant
from video_utils import VideoGenerator
from test_youtube_posting import YouTubeUploader


async def main():
    # Initialize all services
    scraper = TechCrunchScraper()
    telegram_poster = TelegramPoster()
    translator = GroqTranslator(os.environ.get('GROQ_API_KEY'))
    db = ArticleDatabase()
    video_generator = VideoGenerator()
    llm_assistant = LLMVideoAssistant(api_key=os.environ.get('GROQ_API_KEY'))
    x_poster = XPoster()  # Initialize X poster

    # Add these error patterns at the top of main()
    error_patterns = [
        "An unexpected error occurred",
        "Please try again later",
        "یک خطای غیرمنتظره رخ داد",
        "لطفاً بعداً دوباره تلاش کنید"
    ]

    def contains_error_message(text):
        """Check if the text contains any error patterns"""
        return any(pattern in text for pattern in error_patterns)

    try:
        # Add retry mechanism for scraping
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                article_urls = scraper.scrape_articles(limit=10)
                break
            except ConnectionResetError:
                retry_count += 1
                if retry_count == max_retries:
                    raise
                print(f"Connection reset. Retrying... ({retry_count}/{max_retries})")
                await asyncio.sleep(5)

        async def process_article(url, article_data, status):
            """Process a single article for all platforms except Instagram"""
            try:
                # Print the scraped content for inspection
                print(f"\n--- Scraped Content for {url} ---\n{article_data.get('content', '')}\n--- End of Content ---\n")
                # Skip workflow if content is empty
                if not article_data.get('content') or not article_data['content'].strip():
                    print(f"Content is empty for {url}, skipping this article.")
                    return

                # First, try video generation with original English content
                original_content = f"{article_data['title']}\n\n{article_data['content']}"
                try:
                    print(f"Generating video script for: {url}")
                    video_script = llm_assistant.generate_video_script(original_content)
                    if video_script:
                        print("Video script generated, creating video...")
                        video_path = await video_generator.generate_video(
                            content=video_script,
                            use_videos=False,
                            total_duration=30,
                            show_text=True
                        )
                        
                        if video_path:
                            print("Video generated, uploading to YouTube...")
                            youtube_uploader = YouTubeUploader()
                            youtube_response = youtube_uploader.upload_video(
                                video_path=video_path,
                                title=f"Tech News: {article_data['title'][:50]}...",
                                description=original_content[:500]
                            )
                            
                            if youtube_response:
                                print(f"Successfully uploaded to YouTube: {youtube_response['id']}")
                                db.mark_as_posted(url, 'youtube')
                            else:
                                print("Failed to upload to YouTube")
                            
                            if os.path.exists(video_path):
                                os.remove(video_path)
                        else:
                            print("Failed to generate video")
                    else:
                        print("Failed to generate video script")
                    
                except Exception as video_error:
                    print(f"Error in video processing: {video_error}")

                # Now continue with translation and other posting
                translated_title = translator.translate_to_persian(article_data['title'])
                translated_content = translator.translate_to_persian(article_data['content'])
                
                if not translated_title or not translated_content:
                    print(f"Failed to translate content for {url}")
                    return

                # Download image once if needed
                image_path = None
                if article_data.get('image_url'):
                    image_path = await download_image(article_data['image_url'])

                # Post to Telegram
                telegram_success = False
                if not status['telegram']:
                    telegram_result = await telegram_poster.post_to_channel(
                        title=translated_title,
                        content=translated_content,
                        image_url=article_data.get('image_url')
                    )
                    
                    if telegram_result and isinstance(telegram_result, list):
                        print(f"Successfully posted to Telegram: {url}")
                        db.mark_as_posted(url, 'telegram')
                        db.store_message_ids(url, telegram_result)
                        telegram_success = True
                    else:
                        print(f"Failed to post to Telegram: {url}")

                # Post to X (Twitter) if image is available
                x_success = False
                if not status.get('x') and image_path:
                    try:
                        print("Preparing X post content...")
                        
                        # Format content for X with proper length limits
                        title_limit = 100
                        translated_title = translated_title[:title_limit] if translated_title else ""
                        
                        # Calculate remaining space for summary
                        spacing_chars = 2  # for \n\n
                        available_chars = 280 - len(translated_title) - spacing_chars
                        
                        # Get summary within available space
                        x_summary = translator.summarize_for_instagram(
                            translated_content, 
                            max_chars=min(available_chars, 150)
                        )
                        
                        # Combine with proper spacing
                        x_content = f"{translated_title.strip()}\n\n{x_summary.strip()}"
                        
                        # Final length check
                        if len(x_content) > 280:
                            x_content = x_content[:277] + "..."
                        
                        print(f"X Content length: {len(x_content)} chars")
                        
                        # Validate image before posting
                        if os.path.exists(image_path):
                            file_size = os.path.getsize(image_path)
                            if file_size > 5 * 1024 * 1024:  # 5MB limit
                                print(f"Image too large ({file_size/1024/1024:.2f}MB), skipping X post")
                                return
                        else:
                            print(f"Image file not found: {image_path}")
                            return
                        
                        # Post to X with validated content and image
                        x_result = x_poster.post_tweet_with_image(
                            text=x_content,
                            image_path=image_path
                        )
                        
                        if x_result:
                            print(f"Successfully posted to X: {url}")
                            db.mark_as_posted(url, 'x')
                            x_success = True
                        else:
                            print(f"Failed to post to X: {url}")
                            
                    except Exception as e:
                        print(f"Error posting to X: {type(e).__name__} - {str(e)}")
                        if hasattr(e, 'response') and hasattr(e.response, 'text'):
                            print(f"X API Response: {e.response.text}")

                # Only proceed to video generation and YouTube if both Telegram and X succeeded
                if telegram_success and x_success:
                    # First, try video generation with original English content
                    original_content = f"{article_data['title']}\n\n{article_data['content']}"
                    try:
                        print(f"Generating video script for: {url}")
                        video_script = llm_assistant.generate_video_script(original_content)
                        if video_script:
                            print("Video script generated, creating video...")
                            video_path = await video_generator.generate_video(
                                content=video_script,
                                use_videos=False,
                                total_duration=30,
                                show_text=True
                            )
                            
                            if video_path:
                                print("Video generated, uploading to YouTube...")
                                youtube_uploader = YouTubeUploader()
                                youtube_response = youtube_uploader.upload_video(
                                    video_path=video_path,
                                    title=f"Tech News: {article_data['title'][:50]}...",
                                    description=original_content[:500]
                                )
                                
                                if youtube_response:
                                    print(f"Successfully uploaded to YouTube: {youtube_response['id']}")
                                    db.mark_as_posted(url, 'youtube')
                                else:
                                    print("Failed to upload to YouTube")
                                
                                if os.path.exists(video_path):
                                    os.remove(video_path)
                            else:
                                print("Failed to generate video")
                        else:
                            print("Failed to generate video script")
                        
                    except Exception as video_error:
                        print(f"Error in video processing: {video_error}")
                else:
                    print(f"Skipping video generation and YouTube upload for {url} because Telegram or X post failed.")

            except Exception as e:
                print(f"Error processing article {url}: {e}")

        # Process articles
        for url in article_urls:
            try:
                # Check article status
                status = {'telegram': False, 'instagram': False, 'x': False}
                if db.article_exists(url):
                    status = db.get_posting_status(url)
                    if status['telegram'] and status['instagram'] and status['x']:
                        print(f"Article already posted to all platforms: {url}")
                        continue
                    article_data = db.retrieve_article(url)
                else:
                    article_data = scraper.extract_article_data(url)
                    if not article_data:
                        continue
                    db.insert_article(article_data)

                await process_article(url, article_data, status)

            except Exception as e:
                print(f"Error processing article {url}: {e}")
                continue

    finally:
        scraper.quit()
        db.close()

async def download_image(url: str) -> Optional[str]:
    """Download image from URL to temporary file"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    temp_path = f"temp_image_{int(time.time())}.jpg"
                    with open(temp_path, 'wb') as f:
                        f.write(await response.read())
                    return temp_path
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

if __name__ == "__main__":
    asyncio.run(main()) 