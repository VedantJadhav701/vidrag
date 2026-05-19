# Phase 1: Project setup

## Tasks
1. Initialize a `uv` project and add dependencies.
2. Create `.env`, `.gitignore`, and directory structure.
3. Write `config.py`.

## Instructions

### 1.1 Initialise uv project
```bash
uv init vidrag
cd vidrag
```

### 1.2 Add dependencies
```bash
uv add yt-dlp opencv-python-headless google-genai chromadb python-dotenv click gradio pillow tqdm
```

### 1.3 Create .env
```text
GEMINI_API_KEY=your_api_key_here
```
Replace with your real key.

### 1.4 Create .gitignore
```text
.env
__pycache__/
*.pyc
videos/
frames/
chroma_db/
.DS_Store
dist/
*.egg-info/
```

### 1.5 Create required directories
```bash
mkdir -p videos frames chroma_db
```

### 1.6 Create config.py
Copy this exact content into config.py:

```python
"""Configuration constants for VidRAG."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# ChromaDB
CHROMA_PERSIST_DIR = Path("chroma_db")
COLLECTION_NAME = "vidrag_frames"

# Video processing
VIDEO_DIR = Path("videos")
FRAMES_DIR = Path("frames")
FRAME_INTERVAL_SECONDS = 30
TOP_K_RESULTS = 3

# Gemini models
VISION_MODEL = "gemini-2.0-flash"
EMBEDDING_MODEL = "models/text-embedding-004"

# Local models (phase 6)
USE_LOCAL = os.getenv("USE_LOCAL", "false").lower() == "true"
OLLAMA_MODEL = "llava"
OLLAMA_URL = "http://localhost:11434"

# Rate limiting
FRAME_SLEEP_SECONDS = 2
```

### Verification
```bash
python -c "import config; print(config.GEMINI_API_KEY[:5])"
```
Should print the first 5 chars of your key.

### Git commit & push
```bash
git add .
git commit -m "Phase 1: project setup, config, dependencies"
git push origin main
```

Next: phase2_ingestion.md.