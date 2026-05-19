import os
import sys
import uuid
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import chromadb
from google import genai

# Add parent directory to path to import core modules
sys.path.append(str(Path(__file__).parent.parent))

import config
import ingest
import query

app = FastAPI(title="VidRAG API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
# { session_id: { "status": "ingesting" | "ready" | "error", "video_id": str, "collection": str, "error": str } }
sessions: Dict[str, dict] = {}

# WebSocket manager for progress updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)

    async def send_progress(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# Data models
class IngestRequest(BaseModel):
    url: str
    interval: Optional[int] = config.FRAME_INTERVAL_SECONDS

class QueryRequest(BaseModel):
    question: str

# Helper to run ingestion in background
async def run_ingestion(session_id: str, url: str, interval: int):
    async def progress_callback(data: dict):
        await manager.send_progress(session_id, data)
        if data["stage"] == "complete":
            sessions[session_id]["status"] = "ready"
            sessions[session_id]["video_id"] = data["video_id"]
            sessions[session_id]["collection"] = f"vid_{data['video_id']}"

    try:
        # Wrap the sync ingest in a thread to keep FastAPI responsive
        loop = asyncio.get_event_loop()
        config.FRAME_INTERVAL_SECONDS = interval
        # Note: We need a way to pass the async callback to the sync ingest.
        # This is tricky. Let's use an async-safe callback wrapper.
        def sync_callback(data):
            asyncio.run_coroutine_threadsafe(progress_callback(data), loop)

        await loop.run_in_executor(None, ingest.ingest, url, sync_callback)
    except Exception as e:
        sessions[session_id]["status"] = "error"
        sessions[session_id]["error"] = str(e)
        await manager.send_progress(session_id, {"stage": "error", "message": str(e)})

@app.post("/api/sessions")
async def create_session(request: IngestRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"status": "ingesting", "url": request.url}
    
    background_tasks.add_task(run_ingestion, session_id, request.url, request.interval)
    
    return {"session_id": session_id}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.websocket("/ws/progress/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            # Just keep connection open to receive progress
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

@app.post("/api/sessions/{session_id}/ask")
async def ask_question(session_id: str, request: QueryRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["status"] != "ready":
        raise HTTPException(status_code=400, detail="Session is not ready for querying")

    chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    collection = chroma_client.get_collection(session["collection"])
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    # We need to modify query_video to return structured data instead of a formatted string
    # For now, let's call the core functions individually
    q_emb = query.embed_query(client, request.question)
    metas = query.retrieve_frames(collection, q_emb)
    
    if config.USE_LOCAL:
        answer = query.answer_question_local(request.question, metas)
    else:
        answer = query.answer_question(client, request.question, metas)

    sources = []
    for m in metas:
        sources.append({
            "timestamp": m["timestamp"],
            "frame_url": f"/api/frames/{m['video_id']}/{Path(m['frame_path']).name}"
        })

    return {
        "answer": answer,
        "sources": sources
    }

# Serve frames directory as static files
app.mount("/api/frames", StaticFiles(directory=str(config.FRAMES_DIR)), name="frames")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
