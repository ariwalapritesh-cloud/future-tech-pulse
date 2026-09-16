"""
video_builder.py - High-Performance Vertical Video Compositor.
Compiles photorealistic visuals with Ken-Burns motion dynamics,
layers voiceover and tension audio, and burns in viral dynamic subtitles.
Outputs 1080x1920 9:16 MP4 ready for YouTube Shorts, Reels, and Threads.
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any
import static_ffmpeg

static_ffmpeg.add_paths()

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

class VideoBuilder:
    def __init__(self):
        self.width = settings.VIDEO_WIDTH
        self.height = settings.VIDEO_HEIGHT
        self.fps = settings.VIDEO_FPS

    def build_video(
        self,
        scenes: List[Dict[str, Any]],
        voice_audio_path: Path,
        music_audio_path: Path,
        subtitles_ass_path: Path,
        output_video_path: Path,
        total_duration: float
    ) -> Path:
        """
        Assembles 1080x1920 vertical video with motion effects, audio mix, and subtitles.
        """
        logger.info(f"Assembling final vertical video ({total_duration:.2f}s) to {output_video_path}...")
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        
        num_scenes = len(scenes)
        base_scene_duration = total_duration / num_scenes
        
        temp_dir = output_video_path.parent / "temp_clips"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        scene_clip_paths = []
        concat_list_path = temp_dir / "concat_list.txt"

        with open(concat_list_path, "w", encoding="utf-8") as f_concat:
            for idx, scene in enumerate(scenes):
                img_file = settings.VISUALS_DIR / scene["visual_file"]
                clip_out = temp_dir / f"clip_{idx:02d}.mp4"
                
                total_frames = int(base_scene_duration * self.fps) + 5
                # Zoom-in on even scenes, zoom-out on odd scenes
                if idx % 2 == 0:
                    zoom_expr = "min(zoom+0.0012,1.20)"
                else:
                    zoom_expr = "max(1.20-0.0012*on,1.0)"

                filter_complex = (
                    f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                    f"crop={self.width}:{self.height},"
                    f"zoompan=z='{zoom_expr}':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={self.width}x{self.height}:fps={self.fps},"
                    f"format=yuv420p"
                )

                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(img_file),
                    "-vf", filter_complex,
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-t", f"{base_scene_duration:.2f}",
                    "-pix_fmt", "yuv420p",
                    str(clip_out)
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                scene_clip_paths.append(clip_out)
                f_concat.write(f"file '{clip_out.name}'\n")

        # Step 2: Concatenate visual clips
        raw_concat_video = temp_dir / "raw_visuals.mp4"
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            str(raw_concat_video)
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Step 3: Mix voiceover + background music + dynamic subtitles
        if sys.platform == "win32":
            ass_path_escaped = str(subtitles_ass_path).replace("\\", "/").replace(":", "\\:")
        else:
            ass_path_escaped = str(subtitles_ass_path.resolve()).replace(":", "\\:")
        
        final_cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_concat_video),
            "-i", str(voice_audio_path),
            "-i", str(music_audio_path),
            "-filter_complex",
            f"[0:v]subtitles='{ass_path_escaped}'[v];[1:a]volume=1.0[a1];[2:a]volume=0.22[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{total_duration:.2f}",
            str(output_video_path)
        ]

        logger.info("Executing final render with audio ducking and dynamic subtitle burning...")
        subprocess.run(final_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Video assembly complete! Rendered 9:16 Shorts/Reels video at: {output_video_path}")
        return output_video_path

if __name__ == "__main__":
    print("VideoBuilder loaded.")
