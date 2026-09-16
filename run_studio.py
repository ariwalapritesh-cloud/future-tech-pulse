"""
run_studio.py - Master Autonomous Viral Shorts & Reels Pipeline.
"""

import sys
import os

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import asyncio
import json
import logging
import time
from dataclasses import asdict
from pathlib import Path

from config import settings
from src.trend_scout import TrendScout
from src.script_generator import ScriptGenerator
from src.voice_synthesizer import VoiceSynthesizer
from src.caption_generator import CaptionGenerator
from src.video_builder import VideoBuilder
from src.social_publisher import SocialPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    print("\n" + "=" * 70)
    print(" [>] AUTONOMOUS VIRAL SHORTS & REELS STUDIO")
    print("     Ultra-Realistic AI Content Pipeline & Multi-Platform Publisher")
    print("=" * 70 + "\n")

    start_time = time.time()

    # Step 1: Research Trending Topics
    logger.info(">>> STEP 1: Researching Trending Topics & Scoring Virality...")
    scout = TrendScout()
    top_trend = scout.select_top_trend()
    print(f"\n[*] SELECTED TOPIC: {top_trend.title}")
    print(f"[*] Virality Score: {top_trend.virality_score}/100")
    print(f"[*] Catalyst: {top_trend.catalyst}\n")

    # Step 2: Generate Viral Script & SEO
    logger.info(">>> STEP 2: Engineering Retention-Optimized Script & SEO Package...")
    script_gen = ScriptGenerator()
    script_pkg = script_gen.generate_viral_script(top_trend)
    print(f"[*] Script Generated: {len(script_pkg.scenes)} scenes")
    print(f"[*] Hook (0-5s): \"{script_pkg.scenes[0].spoken_text}\"")
    print(f"[*] YouTube Title: {script_pkg.seo.youtube_title}\n")

    # Step 3: Ultra-Realistic Voice & Soundtrack Synthesis
    logger.info(">>> STEP 3: Synthesizing Ultra-Realistic Voiceover & Cinematic Soundtrack...")
    synthesizer = VoiceSynthesizer()
    voice_path = settings.AUDIO_DIR / "voiceover.mp3"
    music_path = settings.AUDIO_DIR / "soundtrack.wav"

    duration, srt_content = await synthesizer.synthesize_speech(
        script_pkg.full_voiceover_script,
        voice_path
    )
    synthesizer.generate_cinematic_soundtrack(duration, music_path)
    print(f"[*] Voiceover Synthesized: {duration:.2f} seconds")
    print(f"[*] Audio Bed Generated: {music_path.name}\n")

    # Step 4: Dynamic Subtitles
    logger.info(">>> STEP 4: Generating High-Retention Dynamic Subtitles...")
    caption_gen = CaptionGenerator(font_name="Arial", font_size=68)
    sub_path = settings.SUBTITLE_PATH
    caption_gen.convert_srt_to_viral_ass(srt_content, sub_path)
    print(f"[*] Dynamic Subtitles Rendered: {sub_path.name}\n")

    # Step 5: Assemble 9:16 Video with Dynamic Motion
    logger.info(">>> STEP 5: Compiling 1080x1920 Vertical Video (Ken Burns + Dual Audio Mix)...")
    video_builder = VideoBuilder()
    scene_dicts = [asdict(s) for s in script_pkg.scenes]
    final_video = video_builder.build_video(
        scenes=scene_dicts,
        voice_audio_path=voice_path,
        music_audio_path=music_path,
        subtitles_ass_path=sub_path,
        output_video_path=settings.FINAL_VIDEO_PATH,
        total_duration=duration
    )
    print(f"\n[+] FINAL VIRAL VIDEO CREATED: {final_video}")
    print(f"    Resolution: {settings.VIDEO_WIDTH}x{settings.VIDEO_HEIGHT} (9:16 Vertical)")
    print(f"    Duration: {duration:.2f}s\n")

    # Step 6: Multi-Platform Social Media Publishing
    logger.info(">>> STEP 6: Multi-Platform Publishing (YouTube, Instagram, Threads)...")
    publisher = SocialPublisher()
    publish_results = publisher.publish_all(final_video, asdict(script_pkg.seo))

    # Save Complete Artifact Bundle
    metadata_bundle = {
        "topic": asdict(top_trend),
        "script": asdict(script_pkg),
        "video_path": str(final_video),
        "duration_seconds": duration,
        "publish_status": publish_results
    }
    with open(settings.METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_bundle, f, indent=2)

    elapsed = time.time() - start_time
    print("=" * 70)
    print(f" [+] PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.1f}s")
    print(f"     Video File: {final_video}")
    print(f"     Metadata & SEO: {settings.METADATA_PATH}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
