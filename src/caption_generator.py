"""
caption_generator.py - Generates high-retention, viral-styled ASS subtitles.
Produces dynamic 2-4 word phrases with bold fonts, high-contrast outlines,
and yellow/cyan highlights optimized for vertical mobile screens.
"""

import re
from pathlib import Path
from typing import List, Dict

class CaptionGenerator:
    def __init__(self, font_name: str = "Arial", font_size: int = 70):
        self.font_name = font_name
        self.font_size = font_size

    def _parse_srt_timestamp(self, ts: str) -> float:
        # Format: 00:00:00,100 -> seconds
        parts = ts.replace(',', '.').split(':')
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])

    def _format_ass_timestamp(self, seconds: float) -> str:
        # Format: H:MM:SS.cs (centiseconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"

    def convert_srt_to_viral_ass(self, srt_content: str, output_ass_path: Path) -> Path:
        """
        Converts SRT subtitles into punchy, high-retention ASS format
        with high contrast borders and attention-grabbing typography.
        """
        ass_header = f"""[Script Info]
Title: Viral Dynamic Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralDefault,{self.font_name},{self.font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,380,1
Style: ViralHighlight,{self.font_name},{int(self.font_size * 1.05)},&H0000E5FF,&H0000FFFF,&H00000000,&H90000000,-1,0,0,0,105,105,1,0,1,6,4,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        # Parse SRT blocks
        blocks = srt_content.strip().split("\n\n")
        dialogue_lines = []

        # Keywords that get special highlight styling
        highlight_keywords = {
            "SCROLLING", "CLOSED", "DOORS", "AI", "WARNING", "160", "MILLION", 
            "RECURSIVE", "47", "SECONDS", "300", "PULL", "PLUG", "DISTRIBUTED", 
            "TRAINING", "DAWN", "LATE", "STOP", "SECRET", "LEAK"
        }

        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if len(lines) < 3:
                continue
            
            # Line 1: index, Line 2: timestamp, Line 3+: text
            time_match = re.match(r"(\d+:\d+:\d+[,\.]\d+)\s*-->\s*(\d+:\d+:\d+[,\.]\d+)", lines[1])
            if not time_match:
                continue
                
            start_sec = self._parse_srt_timestamp(time_match.group(1))
            end_sec = self._parse_srt_timestamp(time_match.group(2))
            text = " ".join(lines[2:]).strip()

            # Break long sentences into 3-5 word chunks for rapid pacing
            words = text.split()
            if not words:
                continue

            chunk_size = 4
            num_chunks = max(1, (len(words) + chunk_size - 1) // chunk_size)
            chunk_duration = (end_sec - start_sec) / num_chunks

            for i in range(num_chunks):
                chunk_words = words[i * chunk_size : (i + 1) * chunk_size]
                c_start = start_sec + i * chunk_duration
                c_end = c_start + chunk_duration
                
                # Check if any word in chunk is a highlight keyword
                has_highlight = any(w.strip(".,!?:;\"'").upper() in highlight_keywords for w in chunk_words)
                style = "ViralHighlight" if has_highlight else "ViralDefault"

                formatted_words = []
                for w in chunk_words:
                    clean = w.strip(".,!?:;\"'").upper()
                    if clean in highlight_keywords:
                        # Add yellow highlight markup {\c&H0022FFFF&}
                        formatted_words.append(f"{{\\c&H0000F6FF&}}{w.upper()}{{\\c&H00FFFFFF&}}")
                    else:
                        formatted_words.append(w.upper())

                caption_text = " ".join(formatted_words)
                start_str = self._format_ass_timestamp(c_start)
                end_str = self._format_ass_timestamp(c_end)
                
                dialogue_lines.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{caption_text}")

        output_ass_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(dialogue_lines) + "\n")

        return output_ass_path

if __name__ == "__main__":
    cg = CaptionGenerator()
    sample_srt = """1
00:00:00,100 --> 00:00:02,800
Stop scrolling. Something just happened behind closed doors.

2
00:00:02,800 --> 00:00:06,500
Last week, a top AI researcher walked out of the lab.
"""
    out = cg.convert_srt_to_viral_ass(sample_srt, Path("test_subs.ass"))
    print("Generated ASS:", out)
