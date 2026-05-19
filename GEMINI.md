# VidRAG – Video RAG with Vision

You are building **VidRAG** – an open-source tool that lets users ask visual questions about YouTube videos.

**Goal:** download a video, extract frames, describe them with vision AI, embed & store in ChromaDB, then answer questions using retrieved frames.

**Tech stack:** Python 3.12, uv, yt-dlp, opencv-python-headless, google-genai, chromadb, click, gradio.

## Execution rules
1. Follow phase files **in numerical order** (0 → 8).
2. After completing each phase, run the verification steps.
3. If verification passes, **immediately commit and push** to the remote repository (see git commands inside each phase).
4. The repo is: `https://github.com/VedantJadhav701/vidrag.git` (branch `main`).

## Coding standards
- Type hints everywhere.
- Docstrings on all public functions.
- All settings from `config.py`.
- Disable ChromaDB telemetry: `os.environ["ANONYMIZED_TELEMETRY"] = "False"` before importing chromadb.
- Use `pathlib.Path` for paths.
- `RETRIEVAL_QUERY` for question embeddings, `RETRIEVAL_DOCUMENT` for frame descriptions.

## Output
- A `vidrag` CLI (via `cli.py`).
- A Gradio web UI (`vidrag serve`).
- A comparison demo in `examples/compare.py`.

Begin with `phase0_repo.md`.