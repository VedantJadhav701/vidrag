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
EMBEDDING_MODEL = "models/gemini-embedding-2"

# Local models (phase 6)
USE_LOCAL = os.getenv("USE_LOCAL", "false").lower() == "true"
OLLAMA_MODEL = "moondream"
OLLAMA_URL = "http://localhost:11434"

# Rate limiting
FRAME_SLEEP_SECONDS = 2

