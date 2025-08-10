# 🧠 Brainrot Research Video Generator

Convert boring research papers into engaging brainrot-style videos using only open-source AI models!

## 🚀 Quick Start

1. **Setup**:
   ```bash
   python setup.py
   ```

2. **Run**:
   ```bash
   python main.py your_research_paper.pdf
   ```

3. **Output**: Find your brainrot video in the `output/` folder!

## 🤖 How It Works

**4-Agent Pipeline**:
1. **PDF Agent** → Extracts text from research paper
2. **Analysis Agent** → Breaks down key concepts (uses Ollama if available)
3. **Script Agent** → Converts to brainrot-style script
4. **Video Agent** → Generates final video with FFmpeg

## 📋 Requirements

- **Python 3.8+**
- **FFmpeg** (required for video generation)
- **espeak** (optional, for better TTS)
- **Ollama** (optional, for better AI analysis)

## 🎯 Features

- ✅ Pure open-source models
- ✅ Minimal setup (just 4 files!)
- ✅ Works offline (with fallbacks)
- ✅ Handles any research PDF
- ✅ Generates 30-second brainrot videos

## 🔧 Architecture

```
PDF → Parse → Analyze → Script → Video
      Agent1   Agent2    Agent3   Agent4
```

Each agent is self-contained and uses different open-source tools for maximum flexibility.

## 🎬 Example Output

Your research paper about "Quantum Computing Algorithms" becomes:

> "Yo fam, this research paper is about to BREAK YOUR BRAIN! 🤯 
> Scientists were like 'we need quantum computers' and honestly? 
> That's kinda sus but also fire 🔥..."

## 🛠️ Customization

Edit `agents.py` to:
- Change brainrot style/language
- Adjust video duration
- Add more visual effects
- Use different AI models

## 📝 License

Open source - use however you want!
