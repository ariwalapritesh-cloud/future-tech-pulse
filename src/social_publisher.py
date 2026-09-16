"""
social_publisher.py - Autonomous Multi-Platform Social Media Publisher.
Handles production-grade OAuth2 and REST publishing across:
- YouTube Shorts (YouTube Data API v3 with automatic OAuth token caching)
- Instagram Reels (Meta Graph API)
- Threads (Meta Threads API)
"""

import json
import logging
import os
import pickle
import requests
from pathlib import Path
from typing import Dict, Any, Optional

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

# Scopes required for uploading YouTube Shorts
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class SocialPublisher:
    def __init__(self):
        self.yt_secrets = Path(settings.YOUTUBE_CLIENT_SECRETS)
        self.yt_token_pickle = settings.BASE_DIR / "config" / "youtube_token.pickle"
        self.ig_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.ig_user_id = settings.INSTAGRAM_ACCOUNT_ID
        self.threads_token = settings.THREADS_ACCESS_TOKEN
        self.threads_user_id = settings.THREADS_USER_ID

    def get_authenticated_youtube_service(self):
        """
        Authenticates via Google OAuth2 and returns an active YouTube API client.
        Caches user credentials in youtube_token.pickle for 100% headless future uploads.
        """
        try:
            from googleapiclient.discovery import build
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
        except ImportError:
            logger.error("Google API client libraries are not installed yet.")
            return None

        credentials = None

        # Check if cached token exists
        if self.yt_token_pickle.exists():
            with open(self.yt_token_pickle, "rb") as token_file:
                credentials = pickle.load(token_file)

        # If credentials are missing or expired, refresh or run flow
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                logger.info("Refreshing expired YouTube OAuth2 token...")
                credentials.refresh(Request())
            else:
                if not self.yt_secrets.exists():
                    logger.warning(f"YouTube client secrets file not found at: {self.yt_secrets}")
                    return None
                
                logger.info("Launching local browser authorization for YouTube...")
                flow = InstalledAppFlow.from_client_secrets_file(str(self.yt_secrets), YOUTUBE_SCOPES)
                credentials = flow.run_local_server(port=0)

            # Cache the token for automated headless runs
            self.yt_token_pickle.parent.mkdir(parents=True, exist_ok=True)
            with open(self.yt_token_pickle, "wb") as token_file:
                pickle.dump(credentials, token_file)
            logger.info("YouTube OAuth2 credentials successfully cached!")

        return build("youtube", "v3", credentials=credentials)

    def publish_to_youtube_shorts(self, video_path: Path, seo: Dict[str, Any], privacy: str = "public") -> Dict[str, Any]:
        """
        Uploads and registers video directly to YouTube Shorts.
        """
        logger.info("[YouTube Shorts] Initiating publishing pipeline...")
        
        service = self.get_authenticated_youtube_service()
        if not service:
            logger.info("[YouTube Shorts] Running in SIMULATION / STAGING mode.")
            return {
                "platform": "YouTube Shorts",
                "status": "STAGED_READY_FOR_UPLOAD",
                "title": seo.get("youtube_title", ""),
                "tags": seo.get("youtube_tags", []),
                "category_id": "28 (Science & Technology)",
                "video_file": str(video_path),
                "next_step": "Place client_secret.json in workspace to publish live."
            }

        from googleapiclient.http import MediaFileUpload

        body = {
            "snippet": {
                "title": seo["youtube_title"],
                "description": seo["youtube_description"],
                "tags": seo["youtube_tags"],
                "categoryId": "28",  # Science & Technology
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
        request = service.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

        logger.info("Uploading video bytes to YouTube Data API...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        live_url = f"https://youtube.com/shorts/{video_id}"
        logger.info(f"✅ Published successfully to YouTube Shorts: {live_url}")
        return {
            "platform": "YouTube Shorts",
            "status": "PUBLISHED",
            "video_id": video_id,
            "url": live_url
        }

    def publish_to_instagram_reels(self, video_url: str, seo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publishes video to Instagram Reels via Meta Graph API.
        Note: Instagram Graph API requires a publicly accessible video URL.
        """
        logger.info("[Instagram Reels] Initiating publishing pipeline...")
        
        if not self.ig_token or not self.ig_user_id:
            logger.info("[Instagram Reels] Running in SIMULATION / STAGING mode.")
            return {
                "platform": "Instagram Reels",
                "status": "STAGED_READY_FOR_UPLOAD",
                "caption": seo.get("instagram_caption", ""),
                "hashtags_count": len(seo.get("instagram_hashtags", [])),
                "next_step": "Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env."
            }

        # Step 1: Create Reel Container
        url = f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": seo["instagram_caption"],
            "access_token": self.ig_token
        }
        res = requests.post(url, data=payload).json()
        creation_id = res.get("id")
        if not creation_id:
            logger.error(f"Failed to create Instagram container: {res}")
            return {"platform": "Instagram Reels", "status": "FAILED", "error": res}

        # Step 2: Publish Container
        publish_url = f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media_publish"
        pub_res = requests.post(publish_url, data={"creation_id": creation_id, "access_token": self.ig_token}).json()
        logger.info(f"✅ Published successfully to Instagram Reels: {pub_res}")
        return {"platform": "Instagram Reels", "status": "PUBLISHED", "post_id": pub_res.get("id")}

    def publish_to_threads(self, text_content: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes post to Meta Threads via Threads API.
        """
        logger.info("[Meta Threads] Initiating publishing pipeline...")
        
        if not self.threads_token or not self.threads_user_id:
            logger.info("[Meta Threads] Running in SIMULATION / STAGING mode.")
            return {
                "platform": "Meta Threads",
                "status": "STAGED_READY_FOR_UPLOAD",
                "text": text_content,
                "next_step": "Set THREADS_ACCESS_TOKEN and THREADS_USER_ID in .env."
            }

        url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads"
        payload = {
            "media_type": "VIDEO" if media_url else "TEXT",
            "text": text_content,
            "access_token": self.threads_token
        }
        if media_url:
            payload["video_url"] = media_url

        res = requests.post(url, data=payload).json()
        creation_id = res.get("id")
        if not creation_id:
            return {"platform": "Meta Threads", "status": "FAILED", "error": res}

        pub_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads_publish"
        pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.threads_token}).json()
        logger.info(f"✅ Published successfully to Threads: {pub_res}")
        return {"platform": "Meta Threads", "status": "PUBLISHED", "thread_id": pub_res.get("id")}

    def publish_all(self, video_path: Path, seo: Dict[str, Any]) -> Dict[str, Any]:
        """Publishes or stages across all 3 platforms."""
        return {
            "youtube": self.publish_to_youtube_shorts(video_path, seo),
            "instagram": self.publish_to_instagram_reels(str(video_path), seo),
            "threads": self.publish_to_threads(seo.get("threads_post", ""), str(video_path))
        }

if __name__ == "__main__":
    pub = SocialPublisher()
    test_seo = {
        "youtube_title": "The AI Warning That Got 160,000,000 Views ⚠️ (Too Late?) #shorts",
        "youtube_description": "Watch until the end. #shorts",
        "youtube_tags": ["ai", "superintelligence", "shorts"],
        "instagram_caption": "Are we ready for what's coming next? 🤖👇",
        "instagram_hashtags": ["#ai", "#shorts"],
        "threads_post": "Classified AI test showed recursive self-improvement in 47 seconds. Are we safe?"
    }
    results = pub.publish_all(settings.FINAL_VIDEO_PATH, test_seo)
    print("\n--- SOCIAL PUBLISHING REPORT ---")
    print(json.dumps(results, indent=2))
