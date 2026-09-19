import json
import logging
import os
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

class VideoScene(BaseModel):
    scene_number: int
    duration_seconds: float
    spoken_text: str
    visual_description: str
    visual_file: str
    sound_fx: str
    transition: str

class SEOPackage(BaseModel):
    youtube_title: str
    youtube_description: str
    youtube_tags: List[str]
    instagram_caption: str
    instagram_hashtags: List[str]
    threads_post: str
    pinned_comment_trigger: str

class ViralScriptPackage(BaseModel):
    topic_id: str
    title: str
    total_target_duration: float
    scenes: List[VideoScene]
    full_voiceover_script: str
    seo: SEOPackage

class ScriptGenerator:
    def __init__(self):
        logger.info("Initializing Dynamic ScriptGenerator engine with Gemini...")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
        self.client = genai.Client(api_key=self.api_key)

    def generate_viral_script(self, trend) -> ViralScriptPackage:
        prompt = f"""
        You are a master short-form video scriptwriter (MrBeast / Hormozi style) and SEO expert.
        Write a hyper-engaging 9:16 vertical video script based on this trending topic:
        Title: {trend.title}
        Catalyst: {trend.catalyst}
        Hook: {trend.emotional_hook}
        Research Points: {', '.join(trend.research_points)}

        REQUIREMENTS:
        1. Create exactly 5 scenes.
        2. Total duration should be between 40 to 50 seconds.
        3. Visual descriptions MUST be detailed, cinematic, photorealistic image generation prompts (e.g. "Ultra-realistic cinematic wide shot of a glowing quantum core in a dark underground lab, unreal engine 5, 8k, volumetric lighting").
        4. Visual file names should be sequentially named: "scene1.jpg", "scene2.jpg", etc.
        5. Provide high-converting SEO metadata for YouTube, Instagram, and Threads.
        6. DO NOT reuse typical tropes from previous videos; make it highly unique to this specific trend.
        """
        
        logger.info("Generating dynamic 5-scene script and SEO package...")
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ViralScriptPackage,
                temperature=0.8
            )
        )
        
        script_pkg = ViralScriptPackage.model_validate_json(response.text)
        
        # Override with trend info to ensure linkage
        script_pkg.topic_id = trend.topic_id
        script_pkg.title = trend.title
        script_pkg.full_voiceover_script = " ".join([s.spoken_text for s in script_pkg.scenes])
        script_pkg.total_target_duration = sum([s.duration_seconds for s in script_pkg.scenes])
        
        logger.info(f"Script generated successfully. Total duration: {script_pkg.total_target_duration:.2f}s")
        return script_pkg
