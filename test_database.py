# test_database.py
import unittest
import os
from database import ArticleDatabase

class TestArticleDatabase(unittest.TestCase):
    def setUp(self):
        # Use an in-memory database for testing
        self.db = ArticleDatabase(':memory:')
        self.sample_article = {
            "url": "https://example.com/test-article",
            "title": "Test Article",
            "content": "This is a test article.",
            "post_datetime": "2023-10-20T12:34:56",
            "image_url": "https://example.com/image.jpg",
            "crawl_datetime": "2023-10-20T12:35:00"
        }
    
    def test_insert_and_check_article(self):
        # Initially, the article should not exist
        exists = self.db.article_exists(self.sample_article['url'])
        self.assertFalse(exists, "Article should not exist yet")
        
        # Insert the article
        self.db.insert_article(self.sample_article)
        
        # Now, the article should exist
        exists = self.db.article_exists(self.sample_article['url'])
        self.assertTrue(exists, "Article should exist after insertion")
    
    def tearDown(self):
        # Close the database connection
        self.db.conn.close()

if __name__ == '__main__':
    unittest.main()
