import json
import logging
import os
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

class ViralTrend(BaseModel):
    topic_id: str
    title: str
    category: str
    virality_score: float
    catalyst: str
    emotional_hook: str
    why_viral: List[str]
    research_points: List[str]
    target_audiences: List[str]

class TrendScout:
    def __init__(self):
        logger.info("Initializing Dynamic TrendScout engine with Gemini...")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
        self.client = genai.Client(api_key=self.api_key)

    def select_top_trend(self, past_topics: List[str] = None) -> ViralTrend:
        """
        Calls Gemini to generate a brand new, highly viral topic, avoiding past topics.
        """
        past_topics_str = ", ".join(past_topics) if past_topics else "None"
        
        prompt = f"""
        You are an expert viral content researcher and trend scout for TikTok, Shorts, and Reels.
        Your job is to discover a cutting-edge, mind-blowing tech, science, AI, or cosmic mystery 
        that will go extremely viral today. 
        
        CRITICAL CONSTRAINT: Do NOT use any of these past topics: [{past_topics_str}]
        
        Requirements:
        - It must feel urgent, controversial, deeply fascinating, or slightly terrifying.
        - The title must be highly clickable.
        - Provide an emotional hook that stops the scroll in 3 seconds.
        - Ensure it's based on plausible near-future tech, recent breakthroughs, or dark science.
        """
        
        logger.info(f"Querying Gemini for a new unique trend... (Excluding past topics: {len(past_topics or [])})")
        
        response = self.client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ViralTrend,
                temperature=0.9
            )
        )
        
        trend = ViralTrend.model_validate_json(response.text)
        logger.info(f"Top Viral Topic Selected: '{trend.title}' (Score: {trend.virality_score}/100)")
        return trend
