"""Local vision and embedding functions using Ollama."""
import ollama
import base64
import config

def describe_frame_local(frame_path: str) -> str:
    with open(frame_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    prompt = (
        "You are a professional video analyst. Examine this frame as if you were writing a forensic report. "
        "List every visible element: objects, people, clothing, text, numbers, colors, lighting, facial expressions, "
        "background details, and any actions. If there is text or a diagram, transcribe it exactly. "
        "If a person is speaking, note their emotion and gesture. "
        "Describe the scene with enough precision that a blind person could imagine it. "
        "Do NOT make assumptions – only describe what is clearly visible."
    )

    response = ollama.chat(
        model=config.OLLAMA_MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img_b64]
        }]
    )
    return response["message"]["content"]

def embed_text_local(text: str) -> list[float]:
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]
