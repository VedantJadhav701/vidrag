"""Video ingestion: download, extract frames, describe, embed, store."""
import time
import json
import os
from pathlib import Path
from typing import Optional, Callable

import yt_dlp
import cv2
import chromadb
from google import genai
from google.genai import types
from tqdm import tqdm

from local_vision import describe_frame_local, embed_text_local

# Disable telemetry before importing chromadb
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import config

def download_video(url: str, progress_callback: Optional[Callable] = None) -> Path:
    """Download a YouTube video and return its local path."""
    if progress_callback:
        progress_callback({"stage": "downloading", "progress": 0.05})
    config.VIDEO_DIR.mkdir(exist_ok=True)
    ydl_opts = {
        "outtmpl": str(config.VIDEO_DIR / "%(id)s.%(ext)s"),
        "format": "mp4",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = Path(ydl.prepare_filename(info))
    if progress_callback:
        progress_callback({"stage": "downloading", "progress": 0.2})
    return video_path

def extract_frames(video_path: Path, interval: int = None, progress_callback: Optional[Callable] = None) -> list[dict]:
    """Extract frames at given interval, return list with timestamp & path."""
    if interval is None:
        interval = config.FRAME_INTERVAL_SECONDS
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    frames = []
    config.FRAMES_DIR.mkdir(exist_ok=True)
    video_id = video_path.stem

    total_secs = int(duration)
    for i, sec in enumerate(tqdm(range(0, total_secs, interval), desc="Extracting frames")):
        if progress_callback:
            prog = 0.2 + (i / (total_secs / interval)) * 0.2
            progress_callback({"stage": "extracting", "progress": prog})
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = config.FRAMES_DIR / f"{video_id}_{sec:06d}.jpg"
        cv2.imwrite(str(frame_path), frame)
        frames.append({"timestamp_sec": sec, "frame_path": str(frame_path)})

    cap.release()
    return frames

def describe_frame(client: genai.Client, frame_path: str) -> str:
    """Use Gemini Vision to describe a single frame."""
    if config.USE_LOCAL:
        return describe_frame_local(frame_path)
    with open(frame_path, "rb") as f:
        img_bytes = f.read()
    response = client.models.generate_content(
        model=config.VISION_MODEL,
        contents=[
            "Describe this video frame in detail, focusing on visible objects, people, text, and actions.",
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
        ],
    )
    return response.text

def embed_text(client: genai.Client, text: str) -> list[float]:
    """Get text embedding using Gemini."""
    if config.USE_LOCAL:
        return embed_text_local(text)
    result = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=text,
        config={"task_type": "RETRIEVAL_DOCUMENT"},
    )
    return result.embeddings[0].values

def format_timestamp(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def ingest(url: str, progress_callback: Optional[Callable] = None) -> tuple[genai.Client, chromadb.Collection]:
    """Run full ingestion pipeline for a YouTube URL."""
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    print(f"Downloading {url}...")
    video_path = download_video(url, progress_callback)
    video_id = video_path.stem

    frames = extract_frames(video_path, config.FRAME_INTERVAL_SECONDS, progress_callback)
    if not frames:
        raise RuntimeError("No frames extracted.")

    chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    collection_name = f"vid_{video_id}"
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass
    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    ids, embeddings, metadatas, documents = [], [], [], []
    total_frames = len(frames)
    for i, frame in enumerate(tqdm(frames, desc="Describing and embedding")):
        if progress_callback:
            prog = 0.4 + (i / total_frames) * 0.55
            progress_callback({
                "stage": "describing", 
                "progress": prog,
                "current_frame": i + 1,
                "total_frames": total_frames
            })
        
        description = describe_frame(client, frame["frame_path"])
        time.sleep(config.FRAME_SLEEP_SECONDS)

        embedding = embed_text(client, description)
        ts = format_timestamp(frame["timestamp_sec"])

        ids.append(f"{video_id}_{frame['timestamp_sec']}")
        embeddings.append(embedding)
        metadatas.append({
            "timestamp_sec": frame["timestamp_sec"],
            "timestamp": ts,
            "frame_path": frame["frame_path"],
            "video_id": video_id,
        })
        documents.append(description)

    collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    # Save video metadata to index.json
    index_path = Path("index.json")
    if index_path.exists():
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {}
    index[video_id] = {
        "title": video_path.stem,
        "collection": collection_name,
        "frames": len(frames),
    }
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

    if progress_callback:
        progress_callback({"stage": "complete", "progress": 1.0, "video_id": video_id})

    print(f"Ingestion complete. Video ID: {video_id}")
    return client, collection
