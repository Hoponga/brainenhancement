"""
Multi-agent system for brainrot video generation
Each agent handles one part of the pipeline using open-source models
"""

import fitz  # PyMuPDF
import requests
import json
from pathlib import Path
from typing import Dict, List
import subprocess
import tempfile
import os

class PDFAgent:
    """Agent 1: Extract text and structure from research PDF"""
    
    def extract_content(self, pdf_path: str) -> Dict:
        """Extract text, title, sections from PDF"""
        doc = fitz.open(pdf_path)
        
        # Extract all text
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        
        # Simple structure extraction
        lines = full_text.split('\n')
        title = lines[0] if lines else "Research Paper"
        
        # Find abstract (simple heuristic)
        abstract = ""
        for i, line in enumerate(lines):
            if 'abstract' in line.lower():
                abstract = ' '.join(lines[i+1:i+10])  # Next 10 lines
                break
        
        return {
            "title": title.strip(),
            "abstract": abstract.strip(),
            "full_text": full_text,
            "length": len(full_text.split())
        }

class AnalysisAgent:
    """Agent 2: Analyze paper content using local LLM"""
    
    def __init__(self):
        # Using Ollama for local LLM (user needs to install)
        self.base_url = "http://localhost:11434"
        
    def analyze_paper(self, content: Dict) -> Dict:
        """Break down paper into key concepts"""
        
        # Prepare analysis prompt
        prompt = f"""
        Analyze this research paper and extract:
        1. Main research question/problem
        2. Key methodology 
        3. Main findings (2-3 points)
        4. Why it matters
        
        Title: {content['title']}
        Abstract: {content['abstract']}
        
        Keep each point to 1-2 sentences max.
        """
        
        try:
            # Try Ollama API (fallback to simple extraction if not available)
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": "llama2",  # or mistral
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                analysis_text = response.json()['response']
            else:
                raise Exception("Ollama not available")
                
        except:
            # Fallback: Simple rule-based analysis
            analysis_text = self._simple_analysis(content)
        
        return {
            "title": content['title'],
            "analysis": analysis_text,
            "word_count": content['length']
        }
    
    def _simple_analysis(self, content: Dict) -> str:
        """Fallback analysis when LLM not available"""
        return f"""
        🔬 Research Problem: This paper investigates {content['title'].lower()}
        
        📊 Key Method: The researchers used experimental/computational approaches
        
        💡 Main Finding: The study reveals important insights about the topic
        
        🌟 Why It Matters: This research advances our understanding and has practical applications
        """

class ScriptAgent:
    """Agent 3: Convert analysis to brainrot-style script"""
    
    def generate_script(self, analysis: Dict) -> Dict:
        """Create detailed brainrot script like Peter Griffin explanations"""
        
        title = analysis['title']
        content = analysis['analysis']
        
        # Extract key details from analysis for in-depth explanation
        script_parts = self._create_detailed_script(title, content)
        
        # Combine into full brainrot script
        script = f"""
        🧠 BRAINROT RESEARCH DEEP DIVE 🧠
        
        [HOOK - 0-5s]
        "Yo chat, this research paper just dropped and it's absolutely UNHINGED! We're about to go DEEP on {title} and trust me, your brain cells are NOT ready for this journey! 🤯"
        
        [PROBLEM SETUP - 5-15s] 
        "{script_parts['problem']} Like bro, imagine if {script_parts['analogy']} - that's basically what these scientists were dealing with! The audacity! 💀"
        
        [METHOD BREAKDOWN - 15-35s]
        "OK so here's where it gets SPICY! {script_parts['method']} They literally said 'we're about to do something that's never been done before' and then ACTUALLY DID IT! The methodology is giving main character energy fr fr 🔥"
        
        [RESULTS EXPLOSION - 35-55s]
        "BUT WAIT, IT GETS CRAZIER! {script_parts['results']} I'm not even kidding when I say this data is more shocking than finding out your favorite influencer is actually 40! The numbers don't lie bestie! 📊💥"
        
        [IMPLICATIONS - 55-75s]
        "{script_parts['impact']} This is literally going to change how we think about EVERYTHING! It's giving 'I just discovered fire' vibes but make it 2024! 🚀"
        
        [TECHNICAL DEEP DIVE - 75-90s]
        "Now let me break down the actual science because we're not just here for the vibes! {script_parts['technical']} See? Science can be bussin when you actually understand it! 🧪"
        
        [OUTRO - 90s]
        "And THAT'S how you turn boring academic papers into content that actually slaps! Drop a 🧠 if your mind is officially blown, and subscribe for more research that hits different! Science is lowkey the best reality TV! ✨"
        """
        
        # Enhanced visual cues for longer video
        visual_cues = [
            "brain explosion with fire effects",
            "confused scientist with question marks", 
            "galaxy brain expanding sequence",
            "data charts flying everywhere",
            "mind blown reaction compilation",
            "rocket launch with rainbow trail",
            "laboratory equipment dancing",
            "brain emoji rain finale"
        ]
        
        return {
            "script": script,
            "duration": 90,  # Longer for detailed explanation
            "visual_cues": visual_cues,
            "style": "detailed_brainrot"
        }
    
    def _create_detailed_script(self, title: str, analysis: str) -> Dict:
        """Extract and enhance details from analysis for script"""
        # Parse analysis content (simple extraction)
        lines = analysis.split('\n')
        
        problem = f"So these absolute legends looked at '{title}' and said 'this ain't it chief, we need answers!'"
        analogy = "trying to explain TikTok to your grandparents but the grandparents are the entire scientific community"
        method = "They pulled out every tool in the scientific toolkit - we're talking experiments, data analysis, the whole nine yards!"
        results = "The data came back and said 'SIKE! Everything you thought you knew? WRONG!'"
        impact = "This research is about to have the scientific community in SHAMBLES (in the best way possible)!"
        technical = "The statistical significance is through the ROOF, the methodology is cleaner than your room should be, and the implications are bigger than the plot twist in your favorite anime!"
        
        # Try to extract actual details if available
        for line in lines:
            if 'method' in line.lower() or 'approach' in line.lower():
                method = f"They used {line.strip().lower()} and honestly? The innovation is SENDING me! 🔬"
            elif 'result' in line.lower() or 'finding' in line.lower():
                results = f"Get this - {line.strip().lower()} I literally cannot even! The data said what it said! 📈"
            elif 'matter' in line.lower() or 'important' in line.lower():
                impact = f"{line.strip()} This is the kind of research that makes you question everything! 🌟"
        
        return {
            'problem': problem,
            'analogy': analogy, 
            'method': method,
            'results': results,
            'impact': impact,
            'technical': technical
        }

class VideoAgent:
    """Agent 4: Generate final brainrot video"""
    
    def create_video(self, script: Dict, output_dir: str) -> str:
        """Create video from script using open-source tools"""
        
        output_path = Path(output_dir) / "brainrot_video.mp4"
        
        # Create simple video with text overlays
        # Using FFmpeg for video generation (most basic approach)
        
        # Generate TTS audio first (using espeak as fallback)
        audio_path = self._generate_audio(script['script'], output_dir)
        
        # Create video with text and basic effects
        video_path = self._create_video_with_text(script, audio_path, str(output_path))
        
        return video_path
    
    def _generate_audio(self, script_text: str, output_dir: str) -> str:
        """Generate TTS audio with proper FFmpeg-compatible format"""
        audio_path = Path(output_dir) / "narration.wav"
        
        # Clean script text for TTS
        clean_text = script_text.replace('🧠', 'brain').replace('🔥', 'fire').replace('🤯', 'mind blown')
        clean_text = ''.join(c for c in clean_text if c.isalnum() or c.isspace() or c in '.,!?')
        
        # Always create a proper WAV file using FFmpeg
        try:
            # Create silent audio with proper format
            subprocess.run([
                'ffmpeg', 
                '-f', 'lavfi', 
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:duration=30',
                '-c:a', 'pcm_s16le',  # Standard WAV format
                '-y', str(audio_path)
            ], check=True, capture_output=True)
            print("✅ Created compatible audio file")
            
            # Try to add TTS if available (optional enhancement)
            self._try_add_tts(clean_text, audio_path)
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ FFmpeg audio creation failed: {e}")
            # Create minimal valid WAV header as final fallback
            self._create_minimal_wav(audio_path)
        
        return str(audio_path)
    
    def _try_add_tts(self, text: str, audio_path: Path):
        """Try to add TTS to existing audio file (optional)"""
        try:
            if os.name == 'nt':
                import pyttsx3
                temp_tts = audio_path.parent / "temp_tts.wav"
                engine = pyttsx3.init()
                engine.save_to_file(text[:500], str(temp_tts))
                engine.runAndWait()
                # Replace silent audio with TTS if successful
                if temp_tts.exists() and temp_tts.stat().st_size > 1000:
                    temp_tts.replace(audio_path)
                    print("✅ Added TTS narration")
        except Exception as e:
            print(f"⚠️ TTS failed, using silent audio: {e}")
    
    def _create_minimal_wav(self, audio_path: Path):
        """Create minimal valid WAV file as final fallback"""
        # Create a minimal 30-second silent WAV file
        import wave
        with wave.open(str(audio_path), 'wb') as wav_file:
            wav_file.setnchannels(2)  # stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            # 30 seconds of silence
            silence = b'\x00\x00' * 44100 * 30 * 2  # stereo
            wav_file.writeframes(silence)
        print("✅ Created minimal WAV fallback")
    
    def _create_video_with_text(self, script: Dict, audio_path: str, output_path: str) -> str:
        """Create video with text overlays using FFmpeg"""
        
        duration = script.get('duration', 90)
        
        try:
            # Create video with multiple text overlays and effects
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=black:size=1920x1080:duration={duration}',  # black background
                '-i', audio_path,  # audio input
                '-vf', (
                    'drawtext=text="🧠 BRAINROT RESEARCH 🧠":fontsize=80:fontcolor=yellow:'
                    'x=(w-text_w)/2:y=100:enable=between(t\,0\,5),' +
                    'drawtext=text="DEEP DIVE INCOMING":fontsize=60:fontcolor=white:'
                    'x=(w-text_w)/2:y=200:enable=between(t\,5\,10),' +
                    'drawtext=text="SCIENCE IS BUSSIN":fontsize=50:fontcolor=lime:'
                    'x=(w-text_w)/2:y=300:enable=between(t\,10\,15)'
                ),
                '-c:v', 'libx264',
                '-c:a', 'aac', 
                '-pix_fmt', 'yuv420p',  # Ensure compatibility
                '-shortest',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video created: {output_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Video generation failed: {e}")
            # Create detailed script file as fallback
            fallback_path = output_path.replace('.mp4', '_detailed_script.txt')
            with open(fallback_path, 'w', encoding='utf-8') as f:
                f.write("🧠 BRAINROT RESEARCH VIDEO SCRIPT 🧠\n")
                f.write("=" * 50 + "\n\n")
                f.write(script['script'])
                f.write("\n\n" + "=" * 50 + "\n")
                f.write(f"Duration: {duration} seconds\n")
                f.write(f"Style: {script.get('style', 'brainrot')}\n")
                f.write("\nVisual Cues:\n")
                for i, cue in enumerate(script.get('visual_cues', []), 1):
                    f.write(f"{i}. {cue}\n")
            print(f"📝 Created detailed script file: {fallback_path}")
            return fallback_path
        
        return output_path
