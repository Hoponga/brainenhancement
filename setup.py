#!/usr/bin/env python3
"""
Setup script for Brainrot Research Video Generator
Installs dependencies and checks system requirements
"""

import subprocess
import sys
import os

def install_python_deps():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg found")
        return True
    except:
        print("❌ FFmpeg not found. Please install:")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        print("   Linux: sudo apt install ffmpeg")
        print("   Mac: brew install ffmpeg")
        return False

def check_espeak():
    """Check if espeak is installed (optional)"""
    try:
        subprocess.run(["espeak", "--version"], capture_output=True, check=True)
        print("✅ espeak found")
        return True
    except:
        print("⚠️ espeak not found (optional for TTS)")
        print("   Windows: Download from http://espeak.sourceforge.net/")
        print("   Linux: sudo apt install espeak")
        print("   Mac: brew install espeak")
        return False

def setup_ollama():
    """Instructions for Ollama setup (optional)"""
    print("\n🤖 Optional: Install Ollama for better AI analysis")
    print("   1. Download from https://ollama.ai/")
    print("   2. Run: ollama pull llama2")
    print("   3. Start: ollama serve")

def main():
    print("🧠 Setting up Brainrot Research Video Generator\n")
    
    # Install Python deps
    install_python_deps()
    
    # Check system requirements
    ffmpeg_ok = check_ffmpeg()
    espeak_ok = check_espeak()
    
    # Setup instructions
    setup_ollama()
    
    print("\n" + "="*50)
    if ffmpeg_ok:
        print("✅ Setup complete! Ready to generate brainrot videos")
        print("\nUsage: python main.py <path_to_pdf>")
    else:
        print("⚠️ Please install FFmpeg to continue")
    
    print("\nExample: python main.py research_paper.pdf")

if __name__ == "__main__":
    main()
