"""Query engine: retrieve relevant frames and answer visual questions."""
from typing import Optional

from google import genai
from google.genai import types
import chromadb

import config
from local_vision import embed_text_local

def embed_query(client: genai.Client, question: str) -> list[float]:
    """Embed user question with RETRIEVAL_QUERY task type."""
    if config.USE_LOCAL:
        return embed_text_local(question)
    result = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=question,
        config={"task_type": "RETRIEVAL_QUERY"},
    )
    return result.embeddings[0].values

def retrieve_frames(collection: chromadb.Collection, query_embedding: list[float],
                    top_k: int = None) -> list[dict]:
    """Retrieve top_k frames and return their metadata."""
    if top_k is None:
        top_k = config.TOP_K_RESULTS
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["metadatas"][0]

def answer_question(client: genai.Client, question: str,
                    retrieved_metadatas: list[dict]) -> str:
    """Ask Gemini Vision to answer question using retrieved frames."""
    image_parts = []
    for meta in retrieved_metadatas:
        with open(meta["frame_path"], "rb") as f:
            img_bytes = f.read()
        image_parts.append(
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        )

    prompt = (
        "You are a precise visual analyst. You have been given several video frames that are the most relevant "
        "to the user's question. Answer the question using ONLY what you see in those frames. "
        "Quote any visible text, describe colors, shapes, and positions. "
        "If the question cannot be answered from the frames, say so clearly. "
        "End your answer with bullet-point citations linking each statement to a frame timestamp."
    )
    contents = [prompt] + image_parts
    response = client.models.generate_content(
        model=config.VISION_MODEL,
        contents=contents,
    )
    return response.text

def answer_question_local(question: str, retrieved_metadatas: list[dict]) -> str:
    """Ask Ollama (LLaVA/Moondream) to answer question using retrieved frames."""
    import ollama, base64
    # Use only the top frame for simplicity
    with open(retrieved_metadatas[0]["frame_path"], "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    response = ollama.chat(
        model=config.OLLAMA_MODEL,
        messages=[{"role": "user", "content": question, "images": [img_b64]}]
    )
    return response["message"]["content"]

def query_video(collection: chromadb.Collection, client: genai.Client,
                question: str) -> str:
    """End-to-end query: embed, retrieve, answer."""
    q_emb = embed_query(client, question)
    metas = retrieve_frames(collection, q_emb)
    if not metas:
        return "No relevant frames found."
    
    if config.USE_LOCAL:
        answer = answer_question_local(question, metas)
    else:
        answer = answer_question(client, question, metas)
        
    citations = "\n".join([f"  - {m['timestamp']} ({m['frame_path']})" for m in metas])
    return f"{answer}\n\nSources:\n{citations}"
