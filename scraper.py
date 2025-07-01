from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

class TechCrunchScraper:
    def __init__(self):
        self.driver = self.setup_driver()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                return driver
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Failed to initialize driver, attempt {attempt + 1}/{max_retries}")
                time.sleep(2)

    def scrape_articles(self, limit=20):
        # Open TechCrunch latest page
        self.driver.get("https://techcrunch.com/latest")
        self.driver.implicitly_wait(10)

        # Accept cookie popup
        self.accept_cookie_popup()

        # Extract article URLs (limit to 20)
        articles = self.driver.find_elements(By.CLASS_NAME, 'loop-card__title-link')
        article_urls = [article.get_attribute('href') for article in articles[:limit]]
        return article_urls

    def accept_cookie_popup(self):
        # Old popup (Didomi)
        try:
            accept_button = self.driver.find_element(By.ID, "didomi-notice-agree-button")
            accept_button.click()
            print("Cookie consent accepted (Didomi).")
            return
        except:
            pass  # Not found, try new popup

        # New popup (OneTrust/FC)
        try:
            # Try to find the new consent button by class and text
            buttons = self.driver.find_elements(By.CSS_SELECTOR, ".fc-button.fc-cta-consent")
            for btn in buttons:
                if "Consent" in btn.text:
                    btn.click()
                    print("Cookie consent accepted (FC).")
                    return
        except Exception as e:
            print(f"Error handling new consent popup: {e}")

        print("Cookie popup not found or already accepted.")

    def extract_article_data(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(10)

        # Accept cookie on article page
        self.accept_cookie_popup()

        try:
            title_element = self.driver.find_element(By.CLASS_NAME, 'wp-block-post-title')
            title = title_element.text

            content_elements = self.driver.find_elements(By.CSS_SELECTOR, '.entry-content p')
            full_article_content = " ".join([element.text for element in content_elements])

            # Print the extracted data
            print(f"Scraped article: {title}")
            print(f"Content length: {len(full_article_content)} characters")

            # Extract image URL
            try:
                image_element = self.driver.find_element(By.CSS_SELECTOR, '.wp-block-post-featured-image img')
                image_url = image_element.get_attribute('src')
            except:
                image_url = None

            # Get post date from <time>
            try:
                date_element = self.driver.find_element(By.TAG_NAME, 'time')
                post_datetime = date_element.get_attribute('datetime')
            except:
                post_datetime = None

            return {
                "title": title,
                "url": url,
                "content": full_article_content,
                "post_datetime": post_datetime,
                "image_url": image_url,
                "crawl_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def extract_article_data_v2(self, url):
        """Extract article data using updated TechCrunch selectors"""
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        
        # Accept cookie on article page
        self.accept_cookie_popup()
        
        try:
            # 1. Title
            title_element = self.driver.find_element(By.CSS_SELECTOR, ".wp-block-post-title")
            title = title_element.text
            
            # 2. Posted Date
            try:
                date_element = self.driver.find_element(By.CSS_SELECTOR, ".wp-block-post-date > time")
                post_datetime = date_element.get_attribute("datetime")
            except:
                post_datetime = None
            
            # 3. Featured Image
            try:
                image_element = self.driver.find_element(By.CSS_SELECTOR, ".wp-block-post-featured-image img")
                image_url = image_element.get_attribute("src")
            except:
                image_url = None
            
            # 4. Author
            try:
                author_element = self.driver.find_element(By.CSS_SELECTOR, ".post-authors-list__author")
                author = author_element.text
            except:
                author = None
            
            # 5. Content (all paragraphs)
            content_elements = self.driver.find_elements(By.CSS_SELECTOR, ".entry-content p")
            full_article_content = " ".join([element.text for element in content_elements])
            
            # 6. Tags
            try:
                tag_elements = self.driver.find_elements(By.CSS_SELECTOR, ".tc23-post-relevant-terms__terms a")
                tags = [tag.text for tag in tag_elements]
            except:
                tags = []

            print(f"Scraped article: {title}")
            print(f"Content length: {len(full_article_content)} characters")
            
            return {
                "title": title,
                "url": url,
                "content": full_article_content,
                "post_datetime": post_datetime,
                "image_url": image_url,
                "author": author,
                "tags": tags,
                "crawl_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def quit(self):
        self.driver.quit()


