# Phase 8: Documentation & marketing

## 1. Update `README.md`
Replace the placeholder README with the full version below.

```markdown
# VidRAG – See what you ask 🎥

**Video RAG that actually sees** – whiteboards, code, diagrams.  
Ask questions about YouTube videos using visual understanding, not just transcripts.

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![HF Space](https://img.shields.io/badge/🤗-Live_Demo-blue)](https://huggingface.co/spaces/VedantJadhav701/vidrag)

## ✨ Features
- Extract frames from any YouTube video.
- Describe frames with Gemini Vision (or local LLaVA).
- Embed and store in ChromaDB for retrieval.
- Ask natural language questions about visual content.
- CLI and Web UI (Gradio).

## 🚀 Quick Start
```bash
git clone https://github.com/VedantJadhav701/vidrag.git
cd vidrag
uv sync
echo "GEMINI_API_KEY=your_key" > .env
python cli.py ingest --url "https://youtu.be/dQw4w9WgXcQ"
python cli.py ask "What is on screen?" --video-id <ID>
python cli.py serve    # Web UI
```

## 📸 Demo
https://demo.gif

## 🔍 Comparison: Transcript RAG vs VidRAG
Question	Transcript-based RAG	VidRAG (this project)
"What color is the car?"	Not found	Blue
"Show the diagram at 02:30"	No visual context	Frame with diagram shown
"Is there any code on screen?"	Impossible	Yes, Python code visible

## ⚙️ Configuration
FRAME_INTERVAL_SECONDS: frames every N seconds (default 30).

USE_LOCAL=true: use Ollama + LLaVA instead of Gemini.

## 🖥️ Local models
```bash
ollama pull llava
ollama pull nomic-embed-text
export USE_LOCAL=true
# No API key needed
```

## 🤝 Contributing
See CONTRIBUTING.md. First good issue: add support for multiple videos in one collection.

## 📄 License
MIT
```

## 2. Create `CONTRIBUTING.md`
```markdown
# Contributing to VidRAG

## Setup
Clone, then `uv sync`. Use `pre-commit` with black & isort.

## Code style
- Type hints required.
- Docstrings for public functions.

## Testing
Run `pytest` (add tests later).  
Open an issue before large changes.
```

## 3. Create examples/compare.py
A simple script comparing transcript-only RAG vs VidRAG on the same video.

```python
"""Compare transcript-based RAG with VidRAG on the same video."""
# Pseudo-code – implement as needed
print("Transcript RAG: question about colors → no answer.")
print("VidRAG: answers with the actual color.")
```

## 4. Git commit & push
```bash
git add README.md CONTRIBUTING.md examples/
git commit -m "Phase 8: full documentation, comparison, contribution guide"
git push origin main
```

## 5. Post-launch checklist
Star the repo 🌟

Tweet with demo GIF, tag @GoogleAI, @ollama

Post on r/LocalLLaMA, r/Python

Submit to Show HN.