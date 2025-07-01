from test_x_posting import XPoster

def test_tweets():
    try:
        # Initialize the X poster
        x_poster = XPoster()
        
        # 1. Test simple text tweet
        print("\n1. Testing text-only tweet...")
        test_message = "Hello 2 World! This is a test tweet 🌎"
        
        response = x_poster.client_v2.create_tweet(text=test_message)
        if response and hasattr(response, 'data'):
            print(f"✅ Text tweet posted successfully! Tweet ID: {response.data['id']}")
        else:
            print("❌ Failed to post text tweet")
            
        # 2. Test tweet with image
        print("\n2. Testing tweet with image...")
        image_path = "assets/researchgeek.png"
        image_message = "Hello World! Testing tweet with image 🖼️"
        
        result = x_poster.post_tweet_with_image(
            text=image_message,
            image_path=image_path
        )
        
        if result:
            print("✅ Image tweet posted successfully!")
        else:
            print("❌ Failed to post image tweet")
            
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
        return False

if __name__ == "__main__":
    test_tweets() 