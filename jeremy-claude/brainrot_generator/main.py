#!/usr/bin/env python3
"""
Brainrot Video Generator
Converts academic research papers into engaging short-form videos
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Optional
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_processor import PDFProcessor
from content_generator import ContentGenerator
from voice_generator import VoiceGenerator
from video_assembler import VideoAssembler


# Configure logging
def setup_logging(verbose: bool = False):
    """Configure logging settings"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('brainrot_generator.log')
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('moviepy').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    

class BrainrotGenerator:
    """Main application class"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._load_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.content_generator = ContentGenerator(
            model=self.config.get('openai_model', 'gpt-4o-mini')
        )
        self.voice_generator = VoiceGenerator(
            service=self.config.get('tts_service', 'openai')
        )
        self.video_assembler = VideoAssembler()
        
        # Create necessary directories
        self._setup_directories()
        
    def _load_config(self) -> dict:
        """Load configuration from file or environment"""
        config = {
            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            'tts_service': os.getenv('TTS_SERVICE', 'openai'),
            'voice': os.getenv('TTS_VOICE', 'nova'),
            'voice_speed': float(os.getenv('TTS_SPEED', '1.0')),
            'max_duration': int(os.getenv('MAX_DURATION', '180')),
            'words_per_caption': int(os.getenv('WORDS_PER_CAPTION', '5')),
            'platform': os.getenv('PLATFORM', 'tiktok')
        }
        
        # Try to load from config file
        config_file = Path('config.json')
        if config_file.exists():
            try:
                with open(config_file) as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                self.logger.warning(f"Could not load config file: {e}")
                
        return config
        
    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            'backgrounds',
            'temp/audio',
            'temp/video',
            'output'
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
    def process_pdf(self, 
                   pdf_path: str,
                   output_name: Optional[str] = None,
                   background_video: Optional[str] = None,
                   voice: Optional[str] = None,
                   platform: Optional[str] = None) -> Optional[str]:
        """
        Process a PDF into a video
        
        Args:
            pdf_path: Path to PDF file
            output_name: Name for output video
            background_video: Specific background to use
            voice: Voice to use for narration
            platform: Target platform
            
        Returns:
            Path to generated video or None
        """
        try:
            self.logger.info(f"Starting processing of {pdf_path}")
            
            # Step 1: Validate and extract PDF text
            print("📄 Validating PDF...")
            is_valid, message = self.pdf_processor.validate_pdf(pdf_path)
            if not is_valid:
                self.logger.error(f"PDF validation failed: {message}")
                print(f"❌ {message}")
                return None
                
            print("📖 Extracting text from PDF...")
            text = self.pdf_processor.extract_text(pdf_path)
            if not text:
                print("❌ Failed to extract text from PDF")
                return None
                
            print(f"✅ Extracted {len(text)} characters")
            
            # Step 2: Generate video script
            print("🤖 Generating engaging script...")
            platform = platform or self.config['platform']
            max_duration = self.config['max_duration']
            
            content = self.content_generator.generate_summary(text, max_duration)
            if not content:
                print("❌ Failed to generate script")
                return None
                
            script = content['script']
            title = content.get('title', 'Research Summary')
            
            # Optimize for platform
            script = self.content_generator.optimize_for_platform(script, platform)
            print(f"✅ Generated script: '{title}'")
            
            # Step 3: Generate captions
            print("📝 Creating captions...")
            captions = self.content_generator.generate_captions(
                script, 
                self.config['words_per_caption']
            )
            
            # Step 4: Generate voice narration
            print("🎙️ Generating narration...")
            voice = voice or self.config['voice']
            voice_speed = self.config['voice_speed']
            
            audio_path = self.voice_generator.generate_audio(
                script,
                voice=voice,
                speed=voice_speed
            )
            
            if not audio_path:
                print("❌ Failed to generate audio")
                return None
                
            print(f"✅ Audio generated ({self.voice_generator.estimate_duration(script, voice_speed):.1f}s)")
            
            # Step 5: Create video
            print("🎬 Creating video...")
            
            # Generate output filename
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_name = Path(pdf_path).stem
                output_name = f"{pdf_name}_{timestamp}.mp4"
                
            output_path = Path('output') / output_name
            
            video_path = self.video_assembler.create_video(
                audio_path=audio_path,
                captions=captions,
                output_path=str(output_path),
                background_video=background_video
            )
            
            if not video_path:
                print("❌ Failed to create video")
                return None
                
            # Clean up temp files
            self._cleanup_temp_files(audio_path)
            
            print(f"✅ Video created successfully: {video_path}")
            
            # Save metadata
            self._save_metadata(video_path, {
                'source_pdf': pdf_path,
                'title': title,
                'script': script,
                'hashtags': content.get('hashtags', ''),
                'platform': platform,
                'voice': voice,
                'duration': self.voice_generator.estimate_duration(script, voice_speed)
            })
            
            return video_path
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}", exc_info=True)
            print(f"❌ Error: {e}")
            return None
            
    def _cleanup_temp_files(self, *file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
            except Exception as e:
                self.logger.warning(f"Could not delete temp file {file_path}: {e}")
                
    def _save_metadata(self, video_path: str, metadata: dict):
        """Save video metadata"""
        try:
            meta_path = Path(video_path).with_suffix('.json')
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save metadata: {e}")
            
    def batch_process(self, pdf_files: list, **kwargs) -> list:
        """
        Process multiple PDFs
        
        Args:
            pdf_files: List of PDF file paths
            **kwargs: Additional arguments for processing
            
        Returns:
            List of generated video paths
        """
        results = []
        total = len(pdf_files)
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📚 Processing {i}/{total}: {pdf_file}")
            video_path = self.process_pdf(pdf_file, **kwargs)
            if video_path:
                results.append(video_path)
                
        print(f"\n✅ Batch processing complete: {len(results)}/{total} successful")
        return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert research papers to engaging short-form videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s research_paper.pdf
  %(prog)s --input paper.pdf --output amazing_discovery.mp4
  %(prog)s --input paper.pdf --voice nova --platform instagram
  %(prog)s --batch papers/*.pdf --platform youtube
  %(prog)s --add-backgrounds videos/*.mp4
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input PDF file path'
    )
    
    parser.add_argument(
        '--input', '-i',
        dest='input_file',
        help='Input PDF file path (alternative)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output video filename'
    )
    
    parser.add_argument(
        '--voice', '-v',
        choices=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        help='Voice for narration (OpenAI voices)'
    )
    
    parser.add_argument(
        '--platform', '-p',
        choices=['tiktok', 'instagram', 'youtube'],
        help='Target platform for optimization'
    )
    
    parser.add_argument(
        '--background', '-b',
        help='Specific background video to use'
    )
    
    parser.add_argument(
        '--batch',
        nargs='+',
        help='Process multiple PDF files'
    )
    
    parser.add_argument(
        '--add-backgrounds',
        nargs='+',
        help='Add video files to backgrounds library'
    )
    
    parser.add_argument(
        '--list-backgrounds',
        action='store_true',
        help='List available background videos'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Load config if provided
    config = None
    if args.config:
        try:
            with open(args.config) as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
            
    # Initialize generator
    try:
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Error: OpenAI API key not found")
            print("Please set OPENAI_API_KEY in your .env file or as an environment variable")
            sys.exit(1)
            
        generator = BrainrotGenerator(config)
        print("✅ Generator initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        if "proxies" in str(e):
            print("This appears to be a version compatibility issue.")
            print("Try running: pip install httpx<0.28.0")
        elif "API key" in str(e):
            print("Make sure OPENAI_API_KEY is set in your .env file or environment")
        sys.exit(1)
        
    # Handle different operations
    if args.add_backgrounds:
        # Add background videos
        count = generator.video_assembler.add_background_videos(args.add_backgrounds)
        print(f"Added {count} background videos")
        
    elif args.list_backgrounds:
        # List available backgrounds
        backgrounds = generator.video_assembler.get_available_backgrounds()
        if backgrounds:
            print("Available background videos:")
            for bg in backgrounds:
                print(f"  - {bg}")
        else:
            print("No background videos available")
            print("Add videos with: --add-backgrounds video1.mp4 video2.mp4")
            
    elif args.batch:
        # Batch processing
        generator.batch_process(
            args.batch,
            voice=args.voice,
            platform=args.platform,
            background_video=args.background
        )
        
    else:
        # Single file processing
        input_file = args.input or args.input_file
        
        if not input_file:
            parser.print_help()
            sys.exit(1)
            
        generator.process_pdf(
            input_file,
            output_name=args.output,
            background_video=args.background,
            voice=args.voice,
            platform=args.platform
        )


if __name__ == '__main__':
    main()