# Brainrot Video Generator

Transform academic research papers into engaging short-form videos with AI narration and captions, perfect for TikTok, Instagram Reels, and YouTube Shorts.

## Features

- **PDF Processing**: Extract and analyze text from research papers
- **AI Summarization**: Generate engaging, accessible scripts using GPT-4
- **Voice Generation**: Natural-sounding AI narration with multiple voice options
- **Auto-Captioning**: Dynamic, word-by-word captions synchronized with narration
- **Background Videos**: Support for custom background videos with automatic cropping/resizing
- **Platform Optimization**: Automatic optimization for TikTok, Instagram, or YouTube
- **Batch Processing**: Process multiple PDFs at once
- **Customizable**: Extensive configuration options for voices, styles, and output

## Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd brainrot_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Add background videos (optional):
```bash
python main.py --add-backgrounds path/to/videos/*.mp4
```

### Basic Usage

Convert a single PDF:
```bash
python main.py research_paper.pdf
```

With custom options:
```bash
python main.py --input paper.pdf --output amazing_discovery.mp4 --voice nova --platform tiktok
```

## Command Line Options

```
usage: main.py [-h] [--input INPUT_FILE] [--output OUTPUT] 
               [--voice {alloy,echo,fable,onyx,nova,shimmer}]
               [--platform {tiktok,instagram,youtube}] 
               [--background BACKGROUND]
               [--batch BATCH [BATCH ...]] 
               [--add-backgrounds ADD_BACKGROUNDS [ADD_BACKGROUNDS ...]]
               [--list-backgrounds] [--verbose] [--config CONFIG]
               [input]

Arguments:
  input                 Input PDF file path

Options:
  --input, -i          Input PDF file path (alternative)
  --output, -o         Output video filename
  --voice, -v          Voice for narration (OpenAI voices)
  --platform, -p       Target platform for optimization
  --background, -b     Specific background video to use
  --batch              Process multiple PDF files
  --add-backgrounds    Add video files to backgrounds library
  --list-backgrounds   List available background videos
  --verbose            Enable verbose logging
  --config             Path to configuration file
```

## Examples

### Single File Processing
```bash
# Basic usage
python main.py research_paper.pdf

# With custom output name
python main.py --input paper.pdf --output "Mind-Blowing Discovery.mp4"

# With specific voice and platform
python main.py paper.pdf --voice echo --platform instagram
```

### Batch Processing
```bash
# Process multiple PDFs
python main.py --batch papers/*.pdf --platform youtube

# Process with consistent settings
python main.py --batch paper1.pdf paper2.pdf paper3.pdf --voice nova
```

### Background Video Management
```bash
# Add background videos
python main.py --add-backgrounds videos/minecraft.mp4 videos/subway_surfers.mp4

# List available backgrounds
python main.py --list-backgrounds

# Use specific background
python main.py paper.pdf --background minecraft.mp4
```

## Configuration

### Environment Variables (.env)

Create a `.env` file from the template:
```bash
cp .env.example .env
```

Key settings:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Text-to-Speech
TTS_SERVICE=openai
TTS_VOICE=nova
TTS_SPEED=1.0

# Video Settings
MAX_DURATION=180
WORDS_PER_CAPTION=5
PLATFORM=tiktok
```

### Configuration File (config.json)

For advanced customization, edit `config.json`:
```json
{
  "openai_model": "gpt-4o-mini",
  "voice": "nova",
  "voice_speed": 1.0,
  "max_duration": 180,
  "caption_style": {
    "fontsize": 85,
    "color": "white",
    "stroke_color": "black"
  }
}
```

## Voice Options

Available OpenAI voices:
- **alloy**: Neutral, balanced tone
- **echo**: Warm, conversational
- **fable**: Expressive, energetic
- **onyx**: Deep, authoritative
- **nova**: Friendly, upbeat (recommended)
- **shimmer**: Soft, gentle

## Platform Specifications

The tool automatically optimizes for different platforms:

| Platform | Max Duration | Optimal Duration | Aspect Ratio |
|----------|-------------|------------------|--------------|
| TikTok   | 3 minutes   | 60 seconds       | 9:16         |
| Instagram| 90 seconds  | 30 seconds       | 9:16         |
| YouTube  | 60 seconds  | 45 seconds       | 9:16         |

## Output

Videos are saved to the `output/` directory with:
- 1080x1920 resolution (9:16 aspect ratio)
- 30 FPS
- H.264 codec
- AAC audio
- Synchronized captions
- Metadata JSON file with script and settings

## Adding Background Videos

The tool supports common video formats (.mp4, .mov, .avi, .webm). Videos are automatically:
- Cropped to 9:16 aspect ratio
- Resized to 1080x1920
- Looped if shorter than narration
- Trimmed if longer than narration

Add your own background videos:
```bash
python main.py --add-backgrounds path/to/video.mp4
```

Popular background video suggestions:
- Minecraft parkour gameplay
- Subway Surfers gameplay
- Satisfying videos (kinetic sand, slime, etc.)
- Nature scenes
- Abstract animations

## Troubleshooting

### Common Issues

1. **"No module named 'openai'"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"OpenAI API key not provided"**
   - Set your API key in `.env` file
   - Or export it: `export OPENAI_API_KEY=your_key_here`

3. **"FFmpeg not found"**
   - Install FFmpeg:
     - macOS: `brew install ffmpeg`
     - Ubuntu: `sudo apt-get install ffmpeg`
     - Windows: Download from [ffmpeg.org](https://ffmpeg.org)

4. **"PDF has no extractable text"**
   - The PDF might be image-based
   - Try using OCR tools to convert to text first

5. **Video has no background**
   - Add background videos: `python main.py --add-backgrounds video.mp4`
   - The tool will create a gradient background if none available

### Logs

Check `brainrot_generator.log` for detailed error messages.

## Advanced Usage

### Custom Configuration

Create a custom config file:
```json
{
  "openai_model": "gpt-4",
  "max_duration": 60,
  "caption_style": {
    "fontsize": 100,
    "color": "yellow"
  }
}
```

Use it:
```bash
python main.py paper.pdf --config my_config.json
```

### Programmatic Usage

```python
from src.pdf_processor import PDFProcessor
from src.content_generator import ContentGenerator
from src.voice_generator import VoiceGenerator
from src.video_assembler import VideoAssembler

# Initialize components
pdf_proc = PDFProcessor()
content_gen = ContentGenerator()
voice_gen = VoiceGenerator()
video_asm = VideoAssembler()

# Process PDF
text = pdf_proc.extract_text("paper.pdf")
script_data = content_gen.generate_summary(text)
audio_path = voice_gen.generate_audio(script_data['script'])
captions = content_gen.generate_captions(script_data['script'])

# Create video
video_path = video_asm.create_video(
    audio_path=audio_path,
    captions=captions,
    output_path="output.mp4"
)
```

## Performance Tips

1. **Batch Processing**: Process multiple PDFs together for efficiency
2. **Background Videos**: Use pre-cropped 9:16 videos to save processing time
3. **Cache Models**: The first run may be slower as models are downloaded
4. **GPU Acceleration**: Install CUDA-enabled packages for faster video processing

## Contributing

Contributions are welcome! Areas for improvement:
- Additional TTS services (ElevenLabs, AWS Polly)
- More caption styles and animations
- Video effects and transitions
- Support for more document formats
- Web interface

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for educational and creative purposes. Please respect copyright laws and always cite original research papers when sharing generated content. The quality of generated content depends on the OpenAI API and may require manual review before publishing.

## Credits

Built with:
- OpenAI GPT & TTS APIs
- MoviePy for video processing
- pdfplumber for PDF extraction
- FFmpeg for media encoding