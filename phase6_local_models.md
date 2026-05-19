# Phase 6: Local model support (Ollama + LLaVA)

Goal: run VidRAG entirely offline.

## 1. Add dependency
```bash
uv add ollama
```

## 2. Ensure config.py contains these lines (they were already added)
```python
USE_LOCAL = os.getenv("USE_LOCAL", "false").lower() == "true"
OLLAMA_MODEL = "llava"
OLLAMA_URL = "http://localhost:11434"
```

## 3. Create local_vision.py
```python
"""Local vision and embedding functions using Ollama."""
import ollama
import base64

def describe_frame_local(frame_path: str) -> str:
    with open(frame_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    response = ollama.chat(
        model="llava",
        messages=[{
            "role": "user",
            "content": "Describe this video frame in detail, focusing on visible objects, people, text, and actions.",
            "images": [img_b64]
        }]
    )
    return response["message"]["content"]

def embed_text_local(text: str) -> list[float]:
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]
```

## 4. Modify ingest.py
At the top, add:

```python
from local_vision import describe_frame_local, embed_text_local
```

Inside describe_frame, add at the very beginning:

```python
if config.USE_LOCAL:
    return describe_frame_local(frame_path)
```

Inside embed_text, add at the very beginning:

```python
if config.USE_LOCAL:
    return embed_text_local(text)
```

## 5. Modify query.py
At the top, add:

```python
from local_vision import embed_text_local
```

Inside embed_query, add:

```python
if config.USE_LOCAL:
    return embed_text_local(question)
```

For answering with local vision, create a helper inside query.py:

```python
def answer_question_local(question, metas):
    import ollama, base64
    # Use only the top frame for simplicity
    with open(metas[0]["frame_path"], "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    response = ollama.chat(
        model="llava",
        messages=[{"role": "user", "content": question, "images": [img_b64]}]
    )
    return response["message"]["content"]
```

In query_video, before calling answer_question, check config.USE_LOCAL and call answer_question_local instead.

### Verification
```bash
ollama pull llava
ollama pull nomic-embed-text
export USE_LOCAL=true
python cli.py ingest --url "https://youtu.be/dQw4w9WgXcQ"
python cli.py ask "What is on screen?" --video-id <ID>
```
Must work without a GEMINI_API_KEY.

### Git commit & push
```bash
git add local_vision.py ingest.py query.py
git commit -m "Phase 6: local model support (Ollama/LLaVA)"
git push origin main
```

Next: phase7_deployment.md.