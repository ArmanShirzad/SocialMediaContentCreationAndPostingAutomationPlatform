import tweepy
from config import Config
import os
import json
import time

class XPoster:
    def __init__(self):
        # Initialize the v2 client
        self.client_v2 = tweepy.Client(
            bearer_token=Config.X_BEARER_TOKEN,
            consumer_key=Config.X_API_KEY,
            consumer_secret=Config.X_API_KEY_SECRET,
            access_token=Config.X_ACCESS_TOKEN,
            access_token_secret=Config.X_ACCESS_TOKEN_SECRET
        )
        
        # We need v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            Config.X_API_KEY,
            Config.X_API_KEY_SECRET,
            Config.X_ACCESS_TOKEN,
            Config.X_ACCESS_TOKEN_SECRET
        )
        self.api_v1 = tweepy.API(auth)
        
        # Rate limit configuration
        self.rate_limit_file = 'x_rate_limits.json'
        self._init_rate_limits()

    def _init_rate_limits(self):
        """Initialize or load rate limits"""
        try:
            with open(self.rate_limit_file, 'r') as f:
                self.limits = json.load(f)
        except FileNotFoundError:
            self.limits = {
                "posts_today": 0,
                "last_reset": time.time(),
                "last_post_time": 0
            }
            self._save_rate_limits()

    def _save_rate_limits(self):
        """Save current rate limits to file"""
        with open(self.rate_limit_file, 'w') as f:
            json.dump(self.limits, f)

    def _check_rate_limits(self) -> bool:
        """Check if we can post based on rate limits"""
        current_time = time.time()
        
        # Reset counter if 24 hours have passed
        if current_time - self.limits['last_reset'] >= 24 * 3600:
            self.limits['posts_today'] = 0
            self.limits['last_reset'] = current_time
            self._save_rate_limits()
        
        # Check if we're within limits
        return self.limits['posts_today'] < 17

    def _update_rate_limits(self):
        """Update rate limits after successful post"""
        self.limits['posts_today'] += 1
        self.limits['last_post_time'] = time.time()
        self._save_rate_limits()

    def post_tweet_with_image(self, text: str, image_path: str) -> bool:
        """Post a tweet with an image using Twitter API v2"""
        if not self._check_rate_limits():
            print("X rate limit reached for today (17/17 posts). Skipping post.")
            return False

        try:
            # First upload the media using v1.1 API
            print("Attempting to upload media using Twitter API v1.1...")
            media = self.api_v1.media_upload(image_path)
            print(f"Successfully uploaded media with ID: {media.media_id}")
            
            # Create tweet payload according to v2 API specifications
            payload = {
                "text": text,
                "media_ids": [str(media.media_id)]  # Pass media_ids directly, not nested in media object
            }
            
            print("Attempting to create tweet using Twitter API v2...")
            response = self.client_v2.create_tweet(**payload)
            
            print(f"Tweet with image posted successfully! Tweet ID: {response.data['id']}")
            self._update_rate_limits()
            return True
            
        except Exception as e:
            print(f"Twitter API Error: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            
            # Add more detailed error handling
            if "403" in str(e):
                print("\nPossible issues:")
                print("1. Check if your API keys have write permissions")
                print("2. Verify your app has OAuth 2.0 with PKCE enabled")
                print("3. Ensure you have tweet.write scope enabled")
                print("4. Check if your developer account is in good standing")
            return False

# Example usage:
if __name__ == "__main__":
    poster = XPoster()
    
    # Post a tweet with an image
    poster.post_tweet_with_image(
        text="Check out this awesome image!",
        image_path="assets/test.jfif"
    )
