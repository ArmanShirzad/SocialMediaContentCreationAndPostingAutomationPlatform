<div align="center">
  <img src="assets/techcrunch.svg" alt="TechCrunchFarsi Workflow Diagram" width="600"/>
</div>

# TechCrunchFarsi

**IMPORTANT:**

This repository does not contain any credentials, API keys, or secrets. All sensitive information must be provided via environment variables. See `.env.example` for the required variables. Copy `.env.example` to `.env` and fill in your own values before running the project.

## Environment Variables

All API keys, tokens, and credentials are loaded from environment variables. This is a security best practice for public repositories.

- Never commit your `.env` file or any secret files to the repository.
- All files containing secrets (such as `client_secret_*.json`, `token.pickle`, `instagram_session.json`, etc.) are gitignored by default.

TechCrunchFarsi is an automated content pipeline that scrapes the latest articles from TechCrunch, translates and summarizes them in Persian, generates videos, and posts the content to multiple platforms including YouTube, Telegram, and X (Twitter). Instagram posting is also supported, but can be skipped if desired.

## Features
- **Automated Scraping:** Fetches the latest articles from TechCrunch.
- **Translation:** Translates articles to Persian using LLM-powered translation.
- **Summarization:** Summarizes content for social media platforms.
- **Video Generation:** Creates videos from article content using stock images or footage.
- **Multi-Platform Posting:** Posts to YouTube, Telegram, X (Twitter), and optionally Instagram.
- **Queue & Rate Limiting:** Handles Instagram posting asynchronously with rate limits.
- **Database Tracking:** Tracks which articles have been posted to which platforms.
- **Scheduler:** Supports scheduled runs every 6 hours.

## Project Structure
```
TechCrunchFarsi/
├── main.py                  # Full workflow (all platforms)
├── main_no_instagram.py     # Workflow without Instagram
├── scraper.py               # TechCrunch scraper
├── telegram_poster.py       # Telegram posting logic
├── test_x_posting.py        # X (Twitter) posting logic
├── test_youtube_posting.py  # YouTube uploading logic
├── instagram_poster.py      # Instagram posting logic
├── instagram_queue.py       # Instagram queue management
├── video_utils.py           # Video generation utilities
├── llm_processor.py         # LLM-based processing (summarization, keywords)
├── translator.py            # Persian translation utilities
├── database.py              # Article database management
├── config/                  # Configuration and session files
├── requirements.txt         # Python dependencies
├── scheduler.py             # Scheduler for periodic runs
├── ...                      # Other utility and test files
```

## Setup
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd TechCrunchFarsi
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/Mac:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure credentials:**
   - Place your Google API client secret JSON in the root directory (for YouTube uploads).
   - Edit files in the `config/` directory as needed (e.g., for blacklists, whitelists, credentials).
   - Set up Telegram and X (Twitter) API credentials as required by the respective poster modules.
   - For Instagram, set credentials in `config.py` if using the full workflow.

## Usage
### Run the Full Workflow (All Platforms)
```sh
python main.py
```

### Run Without Instagram
```sh
python main_no_instagram.py
```

### Schedule Automated Runs
To run the workflow every 6 hours automatically:
```sh
python scheduler.py
```

## Workflow Overview
1. **Scrape** latest TechCrunch articles.
2. **Translate** and **summarize** content in Persian.
3. **Generate video** from article content.
4. **Post** to YouTube, Telegram, and X (Twitter).
5. **(Optional)** Queue and post to Instagram (main.py only).
6. **Track** posting status in the database.

## Configuration
- All configuration files are in the `config/` directory.
- Update API keys, session files, and platform-specific settings as needed.
- Rate limits and session persistence are handled automatically for Instagram and X.

## Testing
- Run test scripts (e.g., `test_all.py`, `test_database.py`, etc.) to verify individual modules.
- Example:
  ```sh
  python test_all.py
  ```

## Contribution
Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.