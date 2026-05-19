"""Configuration constants for VidRAG."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

# Local models (Step 3 Optimization)
USE_LOCAL = os.getenv("USE_LOCAL", "true").lower() == "true"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_URL = "http://localhost:11434"

# Rate limiting
FRAME_SLEEP_SECONDS = 1  # Reduced since we are running local
