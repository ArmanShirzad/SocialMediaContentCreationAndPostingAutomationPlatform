import sqlite3
from datetime import datetime

class ArticleDatabase:
    def __init__(self, db_name="articles.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.ensure_schema()

    def ensure_schema(self):
        # Create the articles table if it doesn't exist
        # Define all columns we need upfront.
        # Using INTEGER for boolean columns (0 or 1).
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            content TEXT,
            post_datetime TEXT,
            image_url TEXT,
            crawl_datetime TEXT,
            message_ids TEXT,
            posted_to_telegram INTEGER DEFAULT 0,
            instagram_posted INTEGER DEFAULT 0,
            instagram_in_progress INTEGER DEFAULT 0,
            instagram_last_attempt TEXT,
            instagram_attempts INTEGER DEFAULT 0,
            x_posted BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP  
        )
        """
        self.conn.execute(create_table_sql)
        self.conn.commit()

        # Ensure all columns exist, if not add them.
        # This is defensive in case the DB existed before without some columns.
        self.try_add_column("articles", "message_ids", "TEXT")
        self.try_add_column("articles", "posted_to_telegram", "INTEGER DEFAULT 0")
        self.try_add_column("articles", "instagram_posted", "INTEGER DEFAULT 0")
        self.try_add_column("articles", "instagram_in_progress", "INTEGER DEFAULT 0")
        self.try_add_column("articles", "instagram_last_attempt", "TEXT")
        self.try_add_column("articles", "instagram_attempts", "INTEGER DEFAULT 0")
        self.try_add_column("articles", "x_posted", "BOOLEAN DEFAULT FALSE")
        self.try_add_column("articles", "created_at", "TEXT")  # Remove the default value for ALTER TAB

    def try_add_column(self, table, column, definition):
        # Add a column if it doesn't exist
        if not self.column_exists(table, column):
            alter_sql = f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            self.conn.execute(alter_sql)
            self.conn.commit()

    def column_exists(self, table, column):
        # Check if a column exists in the table using PRAGMA table_info
        cursor = self.conn.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cursor]
        return column in cols

    def insert_article(self, article_data):
        if 'post_datetime' not in article_data:
            article_data['post_datetime'] = datetime.now().isoformat()

        insert_sql = """
        INSERT OR IGNORE INTO articles (title, url, content, post_datetime, image_url, crawl_datetime)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(insert_sql, (
            article_data['title'],
            article_data['url'],
            article_data['content'],
            article_data['post_datetime'],
            article_data['image_url'],
            article_data['crawl_datetime']
        ))
        self.conn.commit()

    def article_exists(self, url):
        query = "SELECT 1 FROM articles WHERE url = ?"
        result = self.conn.execute(query, (url,))
        return result.fetchone() is not None

    def retrieve_article(self, url):
        query = """
        SELECT title, url, content, post_datetime, image_url, crawl_datetime
        FROM articles
        WHERE url = ?
        """
        result = self.conn.execute(query, (url,)).fetchone()
        if result:
            return {
                "title": result[0],
                "url": result[1],
                "content": result[2],
                "post_datetime": result[3],
                "image_url": result[4],
                "crawl_datetime": result[5]
            }
        return None

    def store_message_ids(self, url, message_ids):
        query = "UPDATE articles SET message_ids = ? WHERE url = ?"
        self.conn.execute(query, (','.join(map(str, message_ids)), url))
        self.conn.commit()

    def mark_as_posted(self, url, platform='telegram'):
        if platform.lower() == 'telegram':
            query = "UPDATE articles SET posted_to_telegram = 1 WHERE url = ?"
        elif platform.lower() == 'instagram':
            query = """
            UPDATE articles 
            SET instagram_posted = 1, instagram_in_progress = 0, instagram_last_attempt = ?
            WHERE url = ?
            """
            self.conn.execute(query, (datetime.now().isoformat(), url))
            self.conn.commit()
            return
        elif platform.lower() == 'x':
            query = "UPDATE articles SET x_posted = TRUE WHERE url = ?"
        else:
            raise ValueError(f"Unknown platform: {platform}")

        self.conn.execute(query, (url,))
        self.conn.commit()

    def get_posting_status(self, url):
        query = """
        SELECT posted_to_telegram, instagram_posted, x_posted
        FROM articles
        WHERE url = ?
        """
        row = self.conn.execute(query, (url,)).fetchone()
        if row:
            return {
                'telegram': bool(row[0]),
                'instagram': bool(row[1]),
                'x': bool(row[2])
            }
        return {'telegram': False, 'instagram': False, 'x': False}

    def is_posted_to_instagram(self, url):
        query = "SELECT instagram_posted FROM articles WHERE url = ?"
        result = self.conn.execute(query, (url,)).fetchone()
        return bool(result and result[0])

    def try_mark_for_instagram_posting(self, url):
        """
        Mark article as in_progress for Instagram posting if it's not already posted or in progress.
        Returns True if successfully marked, False otherwise.
        """
        try:
            # Atomic update
            row = self.conn.execute("""
                SELECT instagram_posted, instagram_in_progress 
                FROM articles
                WHERE url = ?
            """, (url,)).fetchone()

            if not row:
                return False

            posted, in_progress = row
            if posted == 1 or in_progress == 1:
                return False

            self.conn.execute("""
                UPDATE articles
                SET instagram_in_progress = 1, 
                    instagram_attempts = instagram_attempts + 1,
                    instagram_last_attempt = ?
                WHERE url = ?
            """, (datetime.now().isoformat(), url))
            self.conn.commit()
            return self.conn.total_changes > 0
        except Exception as e:
            print(f"Error marking for Instagram posting: {e}")
            return False

    def mark_as_posted_instagram(self, url, success=True):
        """
        Mark the final status of Instagram posting.
        If success is True, instagram_posted = 1.
        If False, just set in_progress = 0 and update last_attempt.
        """
        try:
            posted_val = 1 if success else 0
            self.conn.execute("""
                UPDATE articles
                SET instagram_posted = ?, 
                    instagram_in_progress = 0,
                    instagram_last_attempt = ?
                WHERE url = ?
            """, (posted_val, datetime.now().isoformat(), url))
            self.conn.commit()
        except Exception as e:
            print(f"Error marking as posted to Instagram: {e}")

    def get_instagram_attempts(self, url):
        query = "SELECT instagram_attempts FROM articles WHERE url = ?"
        result = self.conn.execute(query, (url,)).fetchone()
        return result[0] if result else 0

    def close(self):
        self.conn.close()
