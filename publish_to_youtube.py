"""
publish_to_youtube.py - Publish the rendered Short directly to your YouTube Channel.
"""

import json
import logging
from pathlib import Path
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.social_publisher import SocialPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

def main():
    metadata_path = Path("assets/output/metadata.json")
    if not metadata_path.exists():
        logger.error("metadata.json not found! Please run run_studio.py first.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    video_path = Path(meta["video_path"])
    seo = meta["script"]["seo"]

    print("\n" + "=" * 65)
    print(" 🚀 PUBLISHING TO YOUTUBE SHORTS")
    print("=" * 65)
    print(f"🎬 Video File: {video_path.name}")
    print(f"🏷️ Title:      {seo['youtube_title']}")
    print(f"📌 Tags:       {len(seo['youtube_tags'])} tags included")
    print("=" * 65 + "\n")

    publisher = SocialPublisher()
    result = publisher.publish_to_youtube_shorts(video_path, seo, privacy="public")

    print("\n--- RESULT ---")
    print(json.dumps(result, indent=2))
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
