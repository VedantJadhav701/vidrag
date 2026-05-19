# VidRAG SaaS Edition – Polished UI & Session-Based Flow

You are now building the **polished, SaaS‑ready version of VidRAG**.  
The core engine (`ingest.py`, `query.py`) is already built and works. Your job is to design and implement a modern frontend and backend that turns it into a seamless, fast web app.

## 1. Unique Value Proposition (keep top‑of‑mind)
- **Visual‑first** – not just transcripts, it actually sees diagrams, code, whiteboards.
- **Two‑step session**: ingest a video once (with a live progress bar), then ask unlimited questions instantly.
- Works with **cloud (Gemini) or fully local (Ollama)** models.

## 2. User Flow (exactly as they will experience)
1. User lands on the web app (clean landing page).
2. User enters a YouTube URL and clicks **"Ingest Video"**.
3. A **real‑time progress bar** shows four stages: Downloading → Extracting frames → Describing & embedding → Done.
4. Once ingestion finishes, the video is loaded into a session. The UI reveals the **chat interface**.
5. User types a question (e.g., "What's on the whiteboard at 2:10?") and gets an answer **instantly**, with relevant frame thumbnails as sources.
6. User can paste another URL to start a new session, which clears the previous one.

## 3. Tech Stack (modern, production‑ready)
| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14, React, Tailwind CSS, shadcn/ui | Polished UI, responsive, component library |
| **Backend** | FastAPI (Python 3.12) | REST + WebSocket for progress, wraps existing `ingest.py` and `query.py` |
| **Vector DB** | ChromaDB (persistent) | Already built |
| **Deployment** | Frontend: Vercel / Netlify, Backend: Railway / Fly.io / Hugging Face Spaces (Docker) | Public URL |
| **Real‑time progress** | WebSocket from FastAPI to Next.js | Live progress bar updates |

## 4. Backend (FastAPI) API Design
You need to convert the existing CLI logic into these endpoints:

### `POST /api/sessions`
Start a new ingestion session. Body:
```json
{ "url": "https://youtu.be/...", "interval": 30 }
```
Returns:
```json
{ "session_id": "uuid", "video_id": "...", "collection_name": "vid_..." }
```
Immediately starts background ingestion task and streams progress via WebSocket.

### `WS /ws/progress/{session_id}`
Sends JSON messages every step:
```json
{"stage": "downloading", "progress": 0.1}
{"stage": "extracting", "progress": 0.3}
{"stage": "describing", "progress": 0.6, "current_frame": 5, "total_frames": 10}
{"stage": "complete", "progress": 1.0, "session_id": "..."}
```

### `POST /api/sessions/{session_id}/ask`
Body:
```json
{ "question": "What is the background color?" }
```
Returns:
```json
{
  "answer": "The background is blue.",
  "sources": [
    {"timestamp": "00:01:30", "frame_url": "/api/frames/vid_.../frame_000090.jpg"}
  ]
}
```

### `GET /api/frames/{video_id}/{frame_filename}`
Serves the actual JPEG image so the frontend can display thumbnails.

### `GET /api/sessions/{session_id}`
Returns session status (if it's still ingesting or ready).

## 5. Frontend (Next.js) – Key Features
- Landing page with a URL input and "Ingest" button.
- Progress stepper: shows animated steps (Download → Extract → Embed → Ready).
- After ingestion, a chat interface similar to ChatGPT: message list, input box.
- Each answer shows frame thumbnails as citations (use the /api/frames/... endpoint).
- An option to start a new session that resets the UI.

## 6. Implementation Phases
### Phase 9: FastAPI Backend
- Create backend/ folder with FastAPI app.
- Implement session management (in-memory dict or Redis for scale).
- Use ingest.py but modify to report progress through callbacks.
- Add WebSocket endpoint for progress streaming.
- Serve frames static files.

### Phase 10: Next.js Frontend
- Initialize Next.js project with Tailwind and shadcn/ui.
- Build the two‑panel UI: Ingestion panel (hidden after ingestion) and Chat panel.
- Connect WebSocket for live progress.
- Fetch answers from /api/sessions/{session_id}/ask.
- Display sources with image thumbnails.

### Phase 11: Polish & Deploy
- Add loading skeletons, error states.
- Deploy backend to Railway (or a Hugging Face Space with Docker, serving the API).
- Deploy frontend to Vercel, pointing to backend URL.
- Setup environment variables (API keys) on the backend.

## 7. How Users Will Access It
- Public URL: e.g. https://vidrag.vercel.app (frontend) which talks to https://vidrag-api.fly.dev (backend).
- No installation needed – anyone can use it from a browser.
- For self‑hosters, the whole stack can be run with Docker Compose.

## 8. Coding Standards (same as before)
- TypeScript for frontend, type hints for backend.
- Document all API endpoints.
- Keep the existing ingest.py and query.py as they are; import them into FastAPI.

## 9. Deliverable
Fully working SaaS application with the live URL, ready to share with the world.

Now begin with Phase 9.
