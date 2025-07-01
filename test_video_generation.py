import asyncio
from pathlib import Path
from video_utils import VideoGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_video_generation():
    """Test video generation with content"""
    try:
        # Initialize VideoGenerator
        logger.info("Initializing VideoGenerator...")
        generator = VideoGenerator()
        
        # Test content
        test_content = """
        Breaking News: Artificial Intelligence Breakthrough
        Scientists have achieved a major milestone in AI development.
        This discovery promises to revolutionize how we interact with technology.
        The implications for healthcare and education are enormous.
        Experts predict this will transform our daily lives.
        """
        
        # Test 1: Default settings
        logger.info("Test 1: Default video generation...")
        default_video_path = await generator.generate_video(test_content)
        
        if default_video_path:
            logger.info(f"✅ Default video generated at: {default_video_path}")
        else:
            logger.error("❌ Default video generation failed")

     
    except Exception as e:
        logger.error(f"Test failed with error: {e}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_video_generation()) 