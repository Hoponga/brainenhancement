#!/usr/bin/env python3
"""
Brainrot Research Video Generator
Multi-agent pipeline using only open-source models
"""

import os
import sys
from pathlib import Path
from agents import PDFAgent, AnalysisAgent, ScriptAgent, VideoAgent

class BrainrotPipeline:
    def __init__(self):
        self.pdf_agent = PDFAgent()
        self.analysis_agent = AnalysisAgent()
        self.script_agent = ScriptAgent()
        self.video_agent = VideoAgent()
        
    def process_paper(self, pdf_path: str, output_dir: str = "output"):
        """Main pipeline: PDF -> Analysis -> Script -> Video"""
        print(f"🧠 Processing: {pdf_path}")
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Agent 1: Parse PDF
        print("📄 Agent 1: Parsing PDF...")
        paper_content = self.pdf_agent.extract_content(pdf_path)
        
        # Agent 2: Analyze content
        print("🔍 Agent 2: Analyzing content...")
        analysis = self.analysis_agent.analyze_paper(paper_content)
        
        # Agent 3: Generate brainrot script
        print("✍️ Agent 3: Creating brainrot script...")
        script = self.script_agent.generate_script(analysis)
        
        # Agent 4: Generate video
        print("🎬 Agent 4: Generating video...")
        video_path = self.video_agent.create_video(script, output_dir)
        
        print(f"✅ Brainrot video created: {video_path}")
        return video_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    pipeline = BrainrotPipeline()
    pipeline.process_paper(pdf_path)

if __name__ == "__main__":
    main()
