import os
import pickle
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeUploader:
    """
    Automates uploading videos to YouTube with minimal manual re-auth.
    After the initial console-based auth, subsequent runs will refresh 
    tokens automatically using the refresh token.
    """

    def __init__(self):
        # Path to your OAuth client config (from Google Cloud Console)
        self.client_config_file = os.getenv('YOUTUBE_CLIENT_SECRET_FILE', 'client_secret_1031287865484-lfrnbgmvpo4j2rr7g770mmbkrenrgjtt.apps.googleusercontent.com.json')
        # Pickle file to store and reuse credentials
        self.credentials_file = 'token.pickle'
        # OAuth scopes required for uploading YouTube videos
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        # For console-based flow (avoid browser pop-up),
        # you do not need a redirect URI or port.
        # We'll rely on run_console() instead of run_local_server().
        # However, if you want to keep run_local_server, see Variation A below.

    def _load_credentials(self):
        """Load credentials from pickle file, if available."""
        if os.path.exists(self.credentials_file):
            logger.info('Loading existing credentials from token.pickle...')
            with open(self.credentials_file, 'rb') as token:
                return pickle.load(token)
        return None

    def _save_credentials(self, creds):
        """Save refreshed or newly obtained credentials to pickle."""
        logger.info('Saving credentials to token.pickle...')
        with open(self.credentials_file, 'wb') as token:
            pickle.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "token_uri": creds.token_uri,
            }, token)

    def _get_new_credentials_console(self):
        """
        Run a console-based OAuth flow (no browser).
        - You will see a link in the console.
        - Copy-paste the authorization code back into the console.
        """
        # flow = InstalledAppFlow.from_client_secrets_file(
        #     self.client_config_file, 
        #     scopes=self.scopes
        # )
        # # This prints a URL to the console.
        # # Once you open it in a browser and approve, you'll get a code
        # # to paste back into the console. No popup is automatically opened.
        # credentials = flow.run_console()
        # self._save_credentials(credentials)
        # return credentials
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_config_file,
            scopes=self.scopes
            )
        credentials = flow.run_local_server(port=0)  # Browser-based authentication
        self._save_credentials(credentials)  # Save the full credentials object
        logger.info("Refresh token saved successfully.")
        return credentials

    def get_youtube_service(self):
        """
        Returns an authenticated YouTube service object.
        Automatically uses refresh token if available.
        """
    # Load credentials from the refresh token
        credentials = self._load_refresh_token_credentials()

        # If refresh token fails or is missing, run the manual authentication flow
        if not credentials or not credentials.valid:
            logger.info("No valid credentials found. Starting new console flow...")
            credentials = self._get_new_credentials_console()

        return build('youtube', 'v3', credentials=credentials)

    def upload_video(self, video_path, title, description):
        """Upload a video to YouTube using the authenticated service."""
        youtube = self.get_youtube_service()
        if not youtube:
            raise Exception("Failed to get YouTube service")

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Automation", "Tutorial", "Demo"],
                "categoryId": "28"  # e.g., '28' = Science & Technology
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media_file = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            chunksize=-1,
            resumable=True
        )

        logger.info(f"Starting upload of {video_path}...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )
        response = request.execute()
        logger.info(f"Upload Complete! Video ID: {response['id']}")
        return response
    def _load_refresh_token_credentials(self):
        """
        Load credentials using a pre-saved refresh token.
        """
        if not os.path.exists(self.credentials_file):
            logger.error("Credentials file not found. Run the console flow to generate credentials.")
            return None

        with open(self.credentials_file, 'rb') as token:
            data = pickle.load(token)
        
        # Use the saved refresh token to create a credentials object
        creds = Credentials(
            token=None,
            refresh_token=data.get("refresh_token"),
            client_id=data.get("client_id"),
            client_secret=data.get("client_secret"),
            token_uri=data.get("token_uri")
        )

        # Refresh the access token using the refresh token
        try:
            creds.refresh(Request())
            self._save_credentials(creds)  # Save the updated token
            logger.info("Access token refreshed successfully.")
            return creds
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return None


def main():
    """Example usage of YouTubeUploader in a standalone script."""
    video_path = "crud-BDD.mp4"
    video_title = "Automatic Upload Demo"
    video_description = "This video was uploaded automatically using refresh tokens."

    if not os.path.exists(video_path):
        logger.error(f"Video file not found at {video_path}")
        return

    uploader = YouTubeUploader()
    response = uploader.upload_video(video_path, video_title, video_description)

    if response:
        logger.info(f"Video URL: https://youtu.be/{response['id']}")


if __name__ == "__main__":
    main()
