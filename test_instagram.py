import asyncio
import logging
import os
from instagrapi import Client
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_instagram():
    try:
        # Initialize Instagram client
        logger.info("Initializing Instagram client...")
        client = Client()
        
        # Test 1: Basic Login
        logger.info("Test 1: Testing basic Instagram login...")
        try:
            client.login(Config.INSTAGRAM_USERNAME, Config.INSTAGRAM_PASSWORD)
            logger.info("Login successful!")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

        # Test 2: Simple Photo Post
        logger.info("Test 2: Testing basic photo post...")
        try:
            test_image_path = "assets/test.jpg"
            if not os.path.exists(test_image_path):
                logger.warning(f"Test image not found at {test_image_path}")
                # Create a simple test image if none exists
                from PIL import Image
                img = Image.new('RGB', (1080, 1080), color='red')
                os.makedirs('assets', exist_ok=True)
                img.save(test_image_path)
                logger.info("Created test image")

            caption = "Test post from instagrapi\n#test #automation"
            media = client.photo_upload(
                path=test_image_path,
                caption=caption
            )
            logger.info(f"Photo posted successfully! Media ID: {media.id}")

        except Exception as e:
            logger.error(f"Photo posting failed: {e}")
            raise

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        if os.path.exists("assets/test.jpg"):
            os.remove("assets/test.jpg")

if __name__ == "__main__":
    asyncio.run(test_basic_instagram())
    