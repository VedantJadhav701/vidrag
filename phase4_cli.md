# Phase 4: CLI with Click

Create `cli.py` – the main entry point for the `vidrag` commands.

## Code for `cli.py`
```python
"""Command-line interface for VidRAG."""
import json
from pathlib import Path

import click
import chromadb
from google import genai

import config
from ingest import ingest
from query import query_video

INDEX_FILE = Path("index.json")

def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    return {}

@click.group()
def cli():
    """VidRAG – Visual Video Q&A CLI"""
    pass

@cli.command()
@click.option("--url", required=True, help="YouTube URL")
@click.option("--interval", default=config.FRAME_INTERVAL_SECONDS, help="Frame interval in seconds")
def ingest_video(url, interval):
    """Download, extract, index a video."""
    click.echo(f"Ingesting video from {url} (interval={interval}s)")
    config.FRAME_INTERVAL_SECONDS = interval
    client, collection = ingest(url)
    click.echo("Ingestion complete.")

@cli.command()
@click.argument("question")
@click.option("--video-id", required=True, help="Video ID from ingestion")
@click.option("--top-k", default=config.TOP_K_RESULTS)
def ask(question, video_id, top_k):
    """Ask a question about an indexed video."""
    index = load_index()
    if video_id not in index:
        click.echo(f"Video ID '{video_id}' not found. Indexed IDs: {list(index.keys())}")
        return
    collection_name = index[video_id]["collection"]
    chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    try:
        collection = chroma_client.get_collection(collection_name)
    except ValueError:
        click.echo(f"Collection {collection_name} not found. Re-ingest the video.")
        return

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    answer = query_video(collection, client, question)
    click.echo(answer)

@cli.command()
def list_videos():
    """List all indexed videos."""
    index = load_index()
    if not index:
        click.echo("No videos indexed.")
        return
    for vid, info in index.items():
        click.echo(f"ID: {vid} | Frames: {info['frames']} | Collection: {info['collection']}")

@cli.command()
def serve():
    """Launch Gradio web UI."""
    from webui import demo
    demo.launch()

if __name__ == "__main__":
    cli()
```

### Verification
```bash
python cli.py ingest --url "https://youtu.be/dQw4w9WgXcQ"
python cli.py ask "What is the background color?" --video-id <ID_FROM_PREVIOUS>
python cli.py list
```
All commands should succeed.

### Git commit & push
```bash
git add cli.py
git commit -m "Phase 4: CLI with Click (ingest, ask, list, serve)"
git push origin main
```

Next: phase5_webui.md.