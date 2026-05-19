"""Local vision and embedding functions using Ollama."""
import ollama
import base64
import config

def describe_frame_local(frame_path: str) -> str:
    with open(frame_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    response = ollama.chat(
        model=config.OLLAMA_MODEL,
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
