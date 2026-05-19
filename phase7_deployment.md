# Phase 7: Deployment to Hugging Face Spaces

## 1. Create `Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY . .
RUN uv sync
EXPOSE 7860
CMD ["uv", "run", "python", "cli.py", "serve"]
```

## 2. Generate requirements.txt
```bash
uv export --format requirements-txt > requirements.txt
```

## 3. Add a space.yaml (optional)
```yaml
title: VidRAG
emoji: 🎥
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
```

## 4. Git commit & push (this updates the repo)
```bash
git add Dockerfile requirements.txt space.yaml
git commit -m "Phase 7: Hugging Face Spaces deployment files"
git push origin main
```

## 5. Deploy to Hugging Face
Create a new Space at https://huggingface.co/spaces/VedantJadhav701/vidrag (choose Docker SDK).
Then push your existing repo:

```bash
git remote add space https://huggingface.co/spaces/VedantJadhav701/vidrag
git push --force space main
```
Set GEMINI_API_KEY as a secret in the Space settings.

### Verification
Visit https://huggingface.co/spaces/VedantJadhav701/vidrag – the Gradio UI should be live.

Next: phase8_documentation.md.