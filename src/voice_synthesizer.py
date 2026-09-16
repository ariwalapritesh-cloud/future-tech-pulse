"""
voice_synthesizer.py - Ultra-Realistic Neural Speech Synthesis & Timestamps.
Generates broadcast-grade narration with exact subtitle cues
using Microsoft Edge neural voice models.
"""

import asyncio
import logging
import wave
import numpy as np
from pathlib import Path
from typing import Tuple
import edge_tts

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

class VoiceSynthesizer:
    def __init__(self, voice: str = settings.DEFAULT_VOICE, rate: str = settings.VOICE_RATE, pitch: str = settings.VOICE_PITCH):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    async def synthesize_speech(self, text: str, output_audio_path: Path) -> Tuple[float, str]:
        """
        Synthesizes speech to an MP3 file and extracts SRT-formatted cues.
        Returns: (duration_seconds, srt_content)
        """
        logger.info(f"Synthesizing voiceover with voice: {self.voice}")
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
        submaker = edge_tts.SubMaker()
        audio_data = bytearray()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                submaker.feed(chunk)

        with open(output_audio_path, "wb") as f:
            f.write(audio_data)

        srt_content = submaker.get_srt()

        # Calculate duration using ffprobe via static_ffmpeg
        import static_ffmpeg
        static_ffmpeg.add_paths()
        import subprocess
        
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            str(output_audio_path)
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True)
        try:
            duration = float(res.stdout.strip())
        except Exception:
            duration = 38.0  # fallback

        logger.info(f"Voiceover successfully synthesized: {duration:.2f}s duration saved to {output_audio_path}")
        return duration, srt_content

    def generate_cinematic_soundtrack(self, duration_sec: float, output_path: Path):
        """
        Synthesizes a dark cinematic tension audio bed (sub-bass heartbeat pulse + minor chords).
        """
        logger.info(f"Generating cinematic tension soundtrack ({duration_sec:.1f}s)...")
        sample_rate = 44100
        num_samples = int(sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False)
        
        # Sub-bass fundamental (43 Hz)
        bass = 0.35 * np.sin(2 * np.pi * 43.65 * t)
        pulse = 0.5 * (1 + np.sin(2 * np.pi * 1.2 * t))
        bass_pulsing = bass * pulse
        
        # Tension pad harmonic
        pad = (
            0.08 * np.sin(2 * np.pi * 146.83 * t) +
            0.06 * np.sin(2 * np.pi * 174.61 * t) +
            0.05 * np.sin(2 * np.pi * 220.00 * t)
        )
        sweep = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t)
        pad = pad * sweep
        
        mix = bass_pulsing + pad
        fade_len = int(sample_rate * 1.5)
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        
        if len(mix) > 2 * fade_len:
            mix[:fade_len] *= fade_in
            mix[-fade_len:] *= fade_out
            
        mix = mix / np.max(np.abs(mix)) * 0.22
        audio_int16 = (mix * 32767).astype(np.int16)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
            
        logger.info(f"Cinematic tension bed saved to {output_path}")

if __name__ == "__main__":
    synthesizer = VoiceSynthesizer()
    dur, srt = asyncio.run(synthesizer.synthesize_speech("Test sentence for voice synthesis.", settings.AUDIO_DIR / "test.mp3"))
    print(f"Duration: {dur}s")
