![Demo](./assets/SocailMediaAutomationContentandposting.gif)
# SocialMediaContentCreationAndPostingAutomationPlatform

SocialMediaContentCreationAndPostingAutomationPlatform is an automated content pipeline that scrapes the latest articles from a source, translates and summarizes them in another language, post the translated content text and image automatically to Telegram Channel, X & Instagram accounts,   generates video based on the content using Moviepy library and pexels API ,  Instagram posting is also supported, but can be skipped if desired.

## Features
- **Automated Scraping:** Fetches the latest articles from a source in this case is the beloved renowned TechCrunch.
- **Translation:** Translates articles to Persian using LLM-powered translation. u can change just the prompt in groqtranslator.py
- **Summarization:** Summarizes content for social media platforms. each have a limit and the limits and constraints are commented. 
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
<div align="center">
  <img src="assets/techcrunch.svg" alt="TechCrunchFarsi Workflow Diagram" width="600"/>
</div>

The platform orchestrates a robust, multi-stage pipeline for automated content creation and distribution. Here's a detailed breakdown of each step:

1. **Scrape Latest TechCrunch Articles**
   - The scraper fetches the most recent articles from TechCrunch, extracting the title, summary, main content, and associated images. Duplicate detection is performed using the database to avoid reposting the same article.

2. **Translate and Summarize Content in Persian**
   - The content is translated to Persian using an LLM-powered translation engine (Groq API by default). The translation prompt can be customized for other languages or styles in `groqtranslator.py`.
   - Summarization is performed for each target platform, respecting their specific character limits (e.g., Instagram, Telegram, X/Twitter). Summarization logic is modular and can be adapted for other platforms.

3. **AI Voice Generation (Text-to-Speech)**
   - The codebase includes a framework for AI voiceover generation (text-to-speech), designed to integrate with providers such as ElevenLabs or other TTS APIs. 
   - As of now, the TTS feature is a placeholder and not fully implemented or enabled by default. The structure is present for future integration, and you can extend it by connecting your preferred TTS provider and updating the video generation pipeline to include audio narration.
   - If you wish to enable this feature, see the comments and TODOs in `video_utils.py` for integration points.

4. **Generate Video from Article Content**
   - Videos are created using the MoviePy library, combining:
     - Stock images or video clips fetched from the Pexels API based on article keywords.
     - The translated and summarized text, overlaid as captions or subtitles.
     - (Optional) The AI-generated voiceover as the audio track.
   - Video duration, resolution, and branding can be configured in `video_utils.py`.

5. **Post to YouTube, Telegram, and X (Twitter)**
   - The generated video and/or summarized text are posted to:
     - **YouTube:** Video uploads use OAuth2 authentication and refresh tokens for seamless automation.
     - **Telegram:** Posts are sent to a specified channel using the Telegram Bot API.
     - **X (Twitter):** Posts (with or without media) are made using the X API v2 and v1.1 for media uploads.
   - Each platform's API credentials and posting logic are modular and can be extended for other platforms.

6. **(Optional) Queue and Post to Instagram (main.py only)**
   - Instagram posting is handled asynchronously with a queue system to comply with Instagram's strict rate limits and avoid account bans.
   - **Rate Limiting:**
     - Instagram: Maximum posts per hour and minimum interval between posts are enforced (configurable in `instagram_poster.py`).
     - X (Twitter): Daily post limits and cooldowns are tracked and enforced (see `test_x_posting.py`).
     - All rate limits are persisted in local JSON files to survive restarts.
   - The queue system ensures posts are retried if they fail due to temporary errors.

7. **Track Posting Status in the Database**
   - A local database (SQLite or file-based, see `database.py`) tracks which articles have been posted to which platforms, preventing duplicates and enabling robust recovery after interruptions.
   - The database also stores metadata such as post timestamps, platform-specific IDs, and error logs for auditing and troubleshooting.

---

This workflow is fully automated and can be scheduled to run at regular intervals (e.g., every 6 hours) using the included scheduler. All steps are modular, making it easy to add new sources, languages, platforms, or AI features as needed.


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
This project is licensed under Apache 2.0.
