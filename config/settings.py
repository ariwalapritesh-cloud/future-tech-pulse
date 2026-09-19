import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
VISUALS_DIR = ASSETS_DIR / "visuals"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = ASSETS_DIR / "output"

# Video Configuration (Shorts / Reels 9:16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Voice Settings (Ultra-Realistic Edge-TTS neural voice)
# High viral potential voices:
# - en-US-ChristopherNeural (Authoritative, dramatic, documentary)
# - en-US-GuyNeural (Energetic, narrative, conversational)
# - en-US-EricNeural (Deep, serious, cinematic)
DEFAULT_VOICE = os.getenv("TTS_VOICE", "en-US-ChristopherNeural")
VOICE_RATE = os.getenv("TTS_RATE", "+4%")   # slightly punchy for short-form retention
VOICE_PITCH = os.getenv("TTS_PITCH", "-2Hz") # slightly deeper cinematic resonance

# Social Media Credentials (Loaded from environment or .env)
YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", str(BASE_DIR / "client_secret.json"))
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "")
THREADS_USER_ID = os.getenv("THREADS_USER_ID", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Output File Paths
FINAL_AUDIO_PATH = AUDIO_DIR / "voiceover.mp3"
SUBTITLE_PATH = OUTPUT_DIR / "subtitles.ass"
METADATA_PATH = OUTPUT_DIR / "metadata.json"

