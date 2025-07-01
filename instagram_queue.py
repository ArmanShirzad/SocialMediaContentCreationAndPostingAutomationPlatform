import asyncio
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path

@dataclass
class InstagramQueueItem:
    content: str
    url: str
    media_path: Optional[str] = None
    created_at: datetime = datetime.now()

class InstagramQueue:
    def __init__(self, instagram_poster, database):
        self.queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        self.instagram_poster = instagram_poster
        self.current_sleep_task = None
        self.max_retry_attempts = 3
        self.database = database
        self.post_delay = 300  # 5 minutes between posts
        self.retry_delay = 1800  # 30 minutes on failure
        self.shutdown_signal = asyncio.Event()

    async def add_to_queue(self, content: str, url: str, media_path: Optional[str] = None):
        """Add an item to the Instagram posting queue"""
        if not content:
            self.logger.error("Cannot queue empty content")
            return False
            
        # Check if already posted or in progress
        if self.database.is_posted_to_instagram(url):
            self.logger.info(f"Article already posted to Instagram: {url}")
            return False
            
        # Try to mark for posting
        if not self.database.try_mark_for_instagram_posting(url):
            self.logger.info(f"Article already being processed for Instagram: {url}")
            return False
        
        item = InstagramQueueItem(content=content, url=url, media_path=media_path)
        await self.queue.put(item)
        self.logger.info(f"Added new item to Instagram queue. Queue size: {self.queue.qsize()}")
        return True

    async def _sleep_with_cancel_check(self, total_sleep_time: int):
        """Sleep in small increments to allow for cancellation"""
        try:
            sleep_increment = 1  # 1 second increments
            slept_time = 0
            while slept_time < total_sleep_time and self.is_processing:
                await asyncio.sleep(sleep_increment)
                slept_time += sleep_increment
                self.logger.debug(f"Slept for {slept_time}/{total_sleep_time} seconds")
        except asyncio.CancelledError:
            self.logger.debug("Sleep cancelled")
            raise

    async def start_processing(self):
        """Start processing the queue"""
        if self.is_processing:
            self.logger.warning("Queue processing already running")
            return
            
        self.is_processing = True
        self.logger.info("Starting queue processing")
        
        while self.is_processing:
            try:
                # Use wait_for with shorter timeout
                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    # Check shutdown signal
                    if self.shutdown_signal.is_set():
                        self.logger.info("Shutdown signal received")
                        break
                    continue
                
                self.logger.info(f"Processing queue item. Items remaining: {self.queue.qsize()}")
                
                try:
                    success = await self.process_queue_item(item)
                    
                    if success:
                        self.logger.info("Successfully posted item from queue")
                        self.queue.task_done()
                        
                        if self.shutdown_signal.is_set():
                            break
                            
                        self.logger.info(f"Waiting {self.post_delay} seconds before next post")
                        await asyncio.sleep(self.post_delay)
                    else:
                        self.logger.warning("Failed to post item, will retry after delay")
                        await self.queue.put(item)
                        await asyncio.sleep(60)  # Shorter retry delay
                except Exception as e:
                    self.logger.error(f"Error processing queue item: {e}")
                    await self.queue.put(item)
                    await asyncio.sleep(60)
                    
            except Exception as e:
                self.logger.error(f"Error in queue processing loop: {e}")
                await asyncio.sleep(1)
                
        self.logger.info("Queue processing stopped")

    async def stop_processing(self):
        """Stop the queue processing"""
        self.logger.info("Stopping queue processing")
        self.shutdown_signal.set()
        self.is_processing = False
        
        # Cancel any ongoing sleep
        if self.current_sleep_task and not self.current_sleep_task.done():
            self.current_sleep_task.cancel()
            try:
                await self.current_sleep_task
            except asyncio.CancelledError:
                pass

        # Process remaining items with a limit
        retry_count = 0
        while not self.queue.empty() and retry_count < self.max_retry_attempts:
            try:
                item = self.queue.get_nowait()
                self.logger.info("Processing remaining item from queue during shutdown")
                
                # Check rate limiting
                if await self.instagram_poster.can_post():
                    success = await self.process_queue_item(item)
                    if success:
                        self.logger.info("Successfully posted remaining item")
                        self.queue.task_done()
                    else:
                        self.logger.warning("Failed to post remaining item")
                        retry_count += 1
                        if retry_count < self.max_retry_attempts:
                            await self.queue.put(item)
                else:
                    # Put item back and stop processing
                    await self.queue.put(item)
                    break
                    
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                self.logger.error(f"Error processing remaining item: {e}")
                break

        self.logger.info("Queue processing stopped")

    async def process_queue_item(self, item: InstagramQueueItem) -> bool:
        """Process a single queue item"""
        try:
            # Double-check if already posted
            if self.database.is_posted_to_instagram(item.url):
                self.logger.info(f"Item already posted: {item.url}")
                return True

            success = await self.instagram_poster.process_and_post(
                content=item.content,
                media_path=item.media_path
            )

            # If success, mark as posted and DON'T retry
            if success:
                self.database.mark_as_posted_instagram(item.url, success=True)
                self.logger.info(f"Successfully posted and marked in database: {item.url}")
                return True
            
            # Only increment attempts and retry for real failures
            attempts = self.database.get_instagram_attempts(item.url)
            if attempts >= self.max_retry_attempts:
                self.logger.warning(f"Max retry attempts reached for {item.url}")
                self.database.mark_as_posted_instagram(item.url, success=False)
                return True
            
            return False

        except Exception as e:
            self.logger.error(f"Error processing queue item: {e}")
            return False

    async def cleanup_resources(self):
        """Cleanup temporary resources"""
        try:
            # Clean up any queued items' media files
            while not self.queue.empty():
                try:
                    item = self.queue.get_nowait()
                    if item.media_path and os.path.exists(item.media_path):
                        os.remove(item.media_path)
                        self.logger.info(f"Cleaned up media file: {item.media_path}")
                except asyncio.QueueEmpty:
                    break

            # Clean up temp directory
            temp_dir = "temp_image_*"
            for temp_file in Path(".").glob(temp_dir):
                try:
                    os.remove(temp_file)
                    self.logger.info(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up file {temp_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error in cleanup: {e}")
