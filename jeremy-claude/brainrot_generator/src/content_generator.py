"""
Content Generation Module
Handles AI-powered summarization and script generation
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Handles content generation using OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize content generator
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            
        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            if "proxies" in str(e):
                raise ValueError(f"OpenAI client initialization failed due to version compatibility issue. Try: pip install httpx<0.28.0. Error: {e}")
            else:
                raise ValueError(f"Failed to initialize OpenAI client: {e}")
        self.model = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_summary(self, text: str, max_duration: int = 180) -> Optional[Dict[str, str]]:
        """
        Generate engaging video script from research paper text
        
        Args:
            text: Research paper text
            max_duration: Maximum video duration in seconds
            
        Returns:
            Dict with title and script, or None if error
        """
        try:
            # Calculate approximate word count for duration (150 words per minute)
            target_words = int((max_duration / 60) * 150)
            
            prompt = f"""You are creating a viral TikTok/Instagram Reels video script from an academic research paper. 
Your goal is to make complex research accessible and engaging for a general audience.

Research Paper Text:
{text[:8000]}  # Limit context to avoid token limits

Create a video script with these requirements:
1. LENGTH: Approximately {target_words} words ({max_duration} seconds when narrated)
2. STYLE: Conversational, engaging, and slightly dramatic - like popular science communicators
3. HOOK: Start with an attention-grabbing statement or question
4. STRUCTURE:
   - Hook (first 3 seconds must grab attention)
   - Brief context/problem statement
   - Key findings explained simply
   - Why this matters to viewers
   - Call to action (follow for more, share, etc.)
5. LANGUAGE: Simple, accessible, avoid jargon. Use analogies and examples.
6. TONE: Enthusiastic but not overly sensational. Be accurate to the research.

Format your response as JSON with these fields:
{{
    "title": "A catchy, clickbait-style title for the video (max 60 chars)",
    "hook": "The opening hook sentence",
    "script": "The complete narration script",
    "hashtags": "Relevant hashtags for the video"
}}

Remember: This needs to sound natural when spoken aloud, not like reading a paper."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at making academic research accessible and viral on social media."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            import json
            content = json.loads(result)
            
            # Validate required fields
            if not all(key in content for key in ["title", "script"]):
                logger.error("Missing required fields in AI response")
                return None
                
            logger.info(f"Generated script with {len(content['script'].split())} words")
            return content
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
            
    def generate_captions(self, script: str, words_per_caption: int = 5) -> list[Dict[str, Any]]:
        """
        Split script into timed captions
        
        Args:
            script: The narration script
            words_per_caption: Number of words per caption segment
            
        Returns:
            List of caption dictionaries with text and timing
        """
        # Split into words
        words = script.split()
        
        # Group into caption segments
        captions = []
        current_segment = []
        
        for word in words:
            current_segment.append(word)
            
            if len(current_segment) >= words_per_caption:
                captions.append(' '.join(current_segment))
                current_segment = []
                
        # Add remaining words
        if current_segment:
            captions.append(' '.join(current_segment))
            
        # Calculate timing (assuming 150 words per minute)
        words_per_second = 150 / 60
        caption_data = []
        current_time = 0
        
        for caption in captions:
            word_count = len(caption.split())
            duration = word_count / words_per_second
            
            caption_data.append({
                'text': caption,
                'start': current_time,
                'duration': duration,
                'end': current_time + duration
            })
            
            current_time += duration
            
        return caption_data
        
    def optimize_for_platform(self, script: str, platform: str = "tiktok") -> str:
        """
        Optimize script for specific platform
        
        Args:
            script: Original script
            platform: Target platform (tiktok, instagram, youtube)
            
        Returns:
            Optimized script
        """
        platform_limits = {
            "tiktok": {"max_duration": 180, "optimal_duration": 60},
            "instagram": {"max_duration": 90, "optimal_duration": 30},
            "youtube": {"max_duration": 60, "optimal_duration": 45}
        }
        
        if platform not in platform_limits:
            return script
            
        limits = platform_limits[platform]
        
        # Calculate current duration estimate
        word_count = len(script.split())
        estimated_duration = (word_count / 150) * 60
        
        # If within limits, return as is
        if estimated_duration <= limits["optimal_duration"]:
            return script
            
        # Otherwise, truncate to fit
        target_words = int((limits["optimal_duration"] / 60) * 150)
        words = script.split()[:target_words]
        
        # Add ellipsis if truncated
        if len(words) < len(script.split()):
            words.append("...")
            
        return ' '.join(words)