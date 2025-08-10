"""
Voice Generation Module
Handles text-to-speech conversion
"""

import os
import logging
from pathlib import Path
from typing import Optional
from openai import OpenAI
import tempfile

logger = logging.getLogger(__name__)


class VoiceGenerator:
    """Handles AI voice generation"""
    
    def __init__(self, api_key: Optional[str] = None, service: str = "openai"):
        """
        Initialize voice generator
        
        Args:
            api_key: API key for TTS service
            service: TTS service to use (openai, elevenlabs)
        """
        self.service = service
        
        if service == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not provided")
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                if "proxies" in str(e):
                    raise ValueError(f"OpenAI client initialization failed due to version compatibility issue. Try: pip install httpx<0.28.0. Error: {e}")
                else:
                    raise ValueError(f"Failed to initialize OpenAI client: {e}")
        else:
            raise NotImplementedError(f"Service {service} not implemented yet")
            
    def generate_audio(self, 
                      text: str, 
                      output_path: Optional[str] = None,
                      voice: str = "nova",
                      speed: float = 1.0) -> Optional[str]:
        """
        Generate audio from text
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            voice: Voice to use (openai: alloy, echo, fable, onyx, nova, shimmer)
            speed: Speaking speed (0.25 to 4.0)
            
        Returns:
            Path to generated audio file or None if error
        """
        try:
            if self.service == "openai":
                return self._generate_openai(text, output_path, voice, speed)
            else:
                raise NotImplementedError(f"Service {self.service} not implemented")
                
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return None
            
    def _generate_openai(self, 
                        text: str, 
                        output_path: Optional[str],
                        voice: str,
                        speed: float) -> Optional[str]:
        """
        Generate audio using OpenAI TTS
        
        Args:
            text: Text to convert
            output_path: Output file path
            voice: OpenAI voice model
            speed: Speaking speed
            
        Returns:
            Path to audio file
        """
        try:
            # Validate parameters
            if speed < 0.25 or speed > 4.0:
                speed = max(0.25, min(4.0, speed))
                logger.warning(f"Speed adjusted to {speed}")
                
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if voice not in valid_voices:
                logger.warning(f"Invalid voice {voice}, using nova")
                voice = "nova"
                
            # Generate audio
            response = self.client.audio.speech.create(
                model="tts-1-hd",  # Use HD model for better quality
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Save to file
            if not output_path:
                temp_dir = Path("brainrot_generator/temp/audio")
                temp_dir.mkdir(parents=True, exist_ok=True)
                output_path = temp_dir / f"narration_{os.getpid()}.mp3"
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
            # Write audio data
            response.stream_to_file(str(output_path))
            
            logger.info(f"Audio generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            return None
            
    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estimate audio duration based on text length
        
        Args:
            text: Text to be spoken
            speed: Speaking speed multiplier
            
        Returns:
            Estimated duration in seconds
        """
        # Average speaking rate is ~150 words per minute
        word_count = len(text.split())
        base_duration = (word_count / 150) * 60  # Convert to seconds
        
        # Adjust for speed
        actual_duration = base_duration / speed
        
        return actual_duration
        
    def get_voice_options(self) -> dict:
        """
        Get available voice options for current service
        
        Returns:
            Dictionary of voice options
        """
        if self.service == "openai":
            return {
                "alloy": "Neutral, balanced tone",
                "echo": "Warm, conversational",
                "fable": "Expressive, energetic", 
                "onyx": "Deep, authoritative",
                "nova": "Friendly, upbeat (recommended)",
                "shimmer": "Soft, gentle"
            }
        else:
            return {}
            
    def validate_text_length(self, text: str) -> tuple[bool, str]:
        """
        Validate text length for TTS
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not text or len(text.strip()) == 0:
            return False, "Text is empty"
            
        # OpenAI has a 4096 character limit
        if self.service == "openai" and len(text) > 4096:
            return False, f"Text too long ({len(text)} > 4096 characters)"
            
        return True, "Text is valid"