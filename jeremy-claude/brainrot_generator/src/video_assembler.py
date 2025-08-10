"""
Video Assembly Module
Handles video creation with background, audio, and captions
"""

import os
import logging
import random
from pathlib import Path
from typing import Optional, List, Dict, Any
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, CompositeAudioClip
)
from moviepy.video.fx import resize, crop
import numpy as np

logger = logging.getLogger(__name__)


class VideoAssembler:
    """Handles video assembly with captions and audio"""
    
    def __init__(self, backgrounds_dir: str = "brainrot_generator/backgrounds"):
        """
        Initialize video assembler
        
        Args:
            backgrounds_dir: Directory containing background videos
        """
        self.backgrounds_dir = Path(backgrounds_dir)
        self.backgrounds_dir.mkdir(parents=True, exist_ok=True)
        
        # Video settings for vertical format (9:16)
        self.output_width = 1080
        self.output_height = 1920
        self.aspect_ratio = 9/16
        
        # Caption styling
        self.caption_style = {
            'fontsize': 85,
            'font': 'Arial-Bold',
            'color': 'white',
            'stroke_color': 'black',
            'stroke_width': 3,
            'method': 'caption',
            'align': 'center',
            'size': (900, None)  # Width constraint for text wrapping
        }
        
    def create_video(self,
                    audio_path: str,
                    captions: List[Dict[str, Any]],
                    output_path: str,
                    background_video: Optional[str] = None,
                    subtitle_style: Optional[Dict] = None) -> Optional[str]:
        """
        Create final video with all components
        
        Args:
            audio_path: Path to narration audio
            captions: List of caption dictionaries with timing
            output_path: Path for output video
            background_video: Specific background video to use
            subtitle_style: Custom subtitle styling
            
        Returns:
            Path to created video or None if error
        """
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # Get background video
            if not background_video:
                background_video = self._select_background()
                
            if not background_video:
                logger.error("No background video available")
                return None
                
            # Load and prepare background video
            bg_clip = self._prepare_background(background_video, duration)
            
            # Create caption clips
            caption_clips = self._create_caption_clips(captions, subtitle_style)
            
            # Composite everything
            final_video = CompositeVideoClip([bg_clip] + caption_clips)
            
            # Add audio
            final_video = final_video.set_audio(audio)
            
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write video file
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                bitrate='8000k',
                threads=4,
                logger=None  # Suppress moviepy's verbose output
            )
            
            # Clean up
            final_video.close()
            bg_clip.close()
            audio.close()
            
            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
            
    def _select_background(self) -> Optional[str]:
        """
        Select a random background video
        
        Returns:
            Path to background video or None
        """
        video_extensions = ['.mp4', '.mov', '.avi', '.webm']
        videos = []
        
        for ext in video_extensions:
            videos.extend(self.backgrounds_dir.glob(f'*{ext}'))
            
        if not videos:
            logger.warning("No background videos found")
            # Create a default background if none exists
            return self._create_default_background()
            
        selected = random.choice(videos)
        logger.info(f"Selected background: {selected.name}")
        return str(selected)
        
    def _create_default_background(self) -> Optional[str]:
        """
        Create a simple default background video
        
        Returns:
            Path to created background
        """
        try:
            from moviepy.editor import ColorClip
            
            # Create a gradient-like background
            duration = 60  # Default duration
            
            # Create color clip with animated gradient effect
            def make_frame(t):
                # Create gradient that shifts over time
                gradient = np.zeros((self.output_height, self.output_width, 3))
                
                # Purple to blue gradient
                for i in range(self.output_height):
                    ratio = i / self.output_height
                    # Animate the gradient
                    shift = np.sin(t * 0.5) * 0.2
                    
                    gradient[i, :, 0] = int(128 * (1 - ratio + shift))  # R
                    gradient[i, :, 1] = int(64 * (1 - ratio))   # G  
                    gradient[i, :, 2] = int(200 * ratio)        # B
                    
                return gradient.astype('uint8')
                
            clip = VideoFileClip(make_frame, duration=duration)
            clip = clip.set_fps(30)
            
            # Save as default background
            default_path = self.backgrounds_dir / "default_gradient.mp4"
            clip.write_videofile(
                str(default_path),
                codec='libx264',
                fps=30,
                logger=None
            )
            clip.close()
            
            return str(default_path)
            
        except Exception as e:
            logger.error(f"Could not create default background: {e}")
            return None
            
    def _prepare_background(self, video_path: str, duration: float) -> VideoFileClip:
        """
        Prepare background video (crop, resize, loop)
        
        Args:
            video_path: Path to background video
            duration: Required duration
            
        Returns:
            Prepared video clip
        """
        clip = VideoFileClip(video_path)
        
        # Get original dimensions
        w, h = clip.w, clip.h
        original_aspect = w / h
        
        # Resize and crop to 9:16 aspect ratio
        if original_aspect > self.aspect_ratio:
            # Video is wider - crop width
            new_width = int(h * self.aspect_ratio)
            clip = clip.crop(x_center=w/2, width=new_width, height=h)
        else:
            # Video is taller - crop height
            new_height = int(w / self.aspect_ratio)
            clip = clip.crop(y_center=h/2, width=w, height=new_height)
            
        # Resize to output dimensions
        clip = clip.resize((self.output_width, self.output_height))
        
        # Loop or trim to match audio duration
        if clip.duration < duration:
            # Loop the video
            n_loops = int(duration / clip.duration) + 1
            clip = concatenate_videoclips([clip] * n_loops)
            
        # Trim to exact duration
        clip = clip.subclip(0, duration)
        
        return clip
        
    def _create_caption_clips(self, 
                             captions: List[Dict[str, Any]], 
                             custom_style: Optional[Dict] = None) -> List[TextClip]:
        """
        Create caption clips with timing
        
        Args:
            captions: List of caption data
            custom_style: Custom styling options
            
        Returns:
            List of positioned caption clips
        """
        caption_clips = []
        style = self.caption_style.copy()
        
        if custom_style:
            style.update(custom_style)
            
        for caption in captions:
            # Create text clip
            txt_clip = TextClip(
                caption['text'],
                fontsize=style['fontsize'],
                font=style['font'],
                color=style['color'],
                stroke_color=style['stroke_color'],
                stroke_width=style['stroke_width'],
                method=style['method'],
                align=style['align'],
                size=style['size']
            )
            
            # Set timing
            txt_clip = txt_clip.set_start(caption['start'])
            txt_clip = txt_clip.set_duration(caption['duration'])
            
            # Position (center of screen, lower third)
            txt_clip = txt_clip.set_position(('center', 0.7), relative=True)
            
            # Add fade in/out for smooth transitions
            txt_clip = txt_clip.crossfadein(0.2).crossfadeout(0.2)
            
            caption_clips.append(txt_clip)
            
        return caption_clips
        
    def add_background_videos(self, video_paths: List[str]) -> int:
        """
        Add videos to the backgrounds directory
        
        Args:
            video_paths: List of video file paths to add
            
        Returns:
            Number of videos added successfully
        """
        added = 0
        
        for video_path in video_paths:
            try:
                video_path = Path(video_path)
                if not video_path.exists():
                    logger.warning(f"Video not found: {video_path}")
                    continue
                    
                # Copy to backgrounds directory
                import shutil
                dest = self.backgrounds_dir / video_path.name
                shutil.copy2(video_path, dest)
                logger.info(f"Added background video: {video_path.name}")
                added += 1
                
            except Exception as e:
                logger.error(f"Error adding video {video_path}: {e}")
                
        return added
        
    def get_available_backgrounds(self) -> List[str]:
        """
        Get list of available background videos
        
        Returns:
            List of background video filenames
        """
        video_extensions = ['.mp4', '.mov', '.avi', '.webm']
        videos = []
        
        for ext in video_extensions:
            videos.extend([v.name for v in self.backgrounds_dir.glob(f'*{ext}')])
            
        return videos