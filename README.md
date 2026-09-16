# Autonomous Viral Shorts & Reels Studio 🚀

An end-to-end autonomous pipeline engineered to research trending viral topics, generate high-retention vertical scripts, synthesize ultra-realistic neural voiceovers, compile 1080x1920 (9:16) video with motion dynamics and animated subtitles, and publish directly across YouTube Shorts, Instagram Reels, and Threads.

---

## 🌟 Key Features

1. **Trend Discovery & Virality Scoring**:
   - Analyzes breaking frontiers in AI, deep science, tech, and cosmic mysteries.
   - Computes multi-factor virality scores based on emotional hook, curiosity gap, visual potential, and comment velocity.

2. **Retention-Engineered Scriptwriting**:
   - 0-3 second pattern-interrupt hook (stops the scroll).
   - Micro-revelation pacing (scene/motion cut every ~2.5 seconds).
   - High-friction comment trigger designed to flood the comment section and signal algorithms to boost distribution.

3. **Ultra-Realistic Audio Synthesis**:
   - Broadcast-grade Microsoft Neural TTS (`en-US-ChristopherNeural`, `en-US-GuyNeural`).
   - Procedurally generated cinematic sub-bass heartbeat tension soundtrack ducked at -18dB under speech.

4. **Dynamic Animated Captions (Hormozi / MrBeast Style)**:
   - Centered 9:16 vertical placement (safe zone above platform UI).
   - 3-5 word burst cadence with bold typography and yellow/cyan keyword highlights.

5. **Broadcast-Quality 9:16 Compositing**:
   - 1080x1920 60fps vertical output with Ken-Burns motion pan & zoom.
   - Dual audio channel mastering (speech + music bed).
   - Hardcoded ASS subtitle rendering.

6. **Multi-Platform Publisher**:
   - **YouTube Shorts**: YouTube Data API v3 (metadata, tags, privacy, category 28).
   - **Instagram Reels**: Meta Graph API container creation & reel publishing.
   - **Threads**: Meta Threads API cross-posting.
   - **Dry-run simulation mode**: Prepares complete ready-to-upload bundles even if API credentials are not yet configured.

---

## 📁 Project Structure

```
d:\Antigravity\Automation\
├── assets/
│   ├── audio/              # Synthesized voiceover and ambient soundtrack
│   ├── visuals/            # Photorealistic 9:16 scene images
│   └── output/             # Final rendered MP4 video & metadata
├── config/
│   └── settings.py         # Video dimensions, voice profiles, credentials
├── src/
│   ├── trend_scout.py      # Trend scout & viral scoring
│   ├── script_generator.py # Script & multi-platform SEO generator
│   ├── voice_synthesizer.py# Neural voice synthesis & procedural audio bed
│   ├── caption_generator.py# Dynamic ASS subtitle generator
│   ├── video_builder.py    # FFmpeg 9:16 motion compositor
│   └── social_publisher.py # Multi-platform automated publishing
├── run_studio.py           # Master one-click pipeline runner
└── requirements.txt        # Python dependencies
```

---

## 🚀 Quick Start

### 1. Execute the Pipeline
Run the autonomous studio with one command:
```powershell
.\.venv\Scripts\python.exe run_studio.py
```

### 2. Output
- **Rendered Video**: `assets/output/viral_shorts_superintelligence.mp4`
- **Metadata & Copy**: `assets/output/metadata.json`
- **Audio Files**: `assets/audio/voiceover.mp3`, `assets/audio/soundtrack.wav`

---

## 🔑 Publishing to Social Platforms

Copy `.env.example` to `.env` and fill in your platform keys:
- **YouTube Shorts**: Place your OAuth `client_secret.json` in the root directory.
- **Instagram Reels**: Add your `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID`.
- **Threads**: Add your `THREADS_ACCESS_TOKEN` and `THREADS_USER_ID`.

When keys are not provided, the studio operates in **SIMULATION MODE**, generating formatted titles, descriptions, hashtags, and upload cards ready for instant 1-click manual upload or automated staging.
