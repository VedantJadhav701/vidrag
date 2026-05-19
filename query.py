"""Query engine: retrieve relevant frames and answer visual questions."""
from typing import Optional

from google import genai
from google.genai import types
import chromadb

import config
from local_vision import embed_text_local

def embed_query(client: genai.Client, question: str, emb_model: str = "gemini") -> list[float]:
    """Embed user question with specified model."""
    if config.USE_LOCAL or emb_model == "local":
        return embed_text_local(question)
    try:
        result = client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=question,
            config={"task_type": "RETRIEVAL_QUERY"},
        )
        return result.embeddings[0].values
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "resource_exhausted" in err_msg:
            print("Embedding API limit reached. Falling back to local embedding for query.")
            return embed_text_local(question)
        raise e

def retrieve_frames(collection: chromadb.Collection, query_embedding: list[float],
                    top_k: int = None) -> list[dict]:
    """Retrieve top_k frames and return their metadata."""
    if top_k is None:
        top_k = config.TOP_K_RESULTS
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["metadatas"][0]

def answer_question(client: genai.Client, question: str,
                    retrieved_metadatas: list[dict]) -> str:
    """Ask Gemini Vision to answer question using retrieved frames with explicit timestamps."""
    if config.USE_LOCAL:
        return answer_question_local(question, retrieved_metadatas)

    contents = [
        "You are a precise visual analyst. You have been given several video frames with their timestamps. "
        "Answer the question using ONLY what you see in these specific frames. "
        "Quote any visible text, describe colors, shapes, and positions. "
        "End your answer with bullet-point citations using the EXACT timestamps provided for each frame (e.g., [HH:MM:SS])."
    ]
    
    for meta in retrieved_metadatas:
        with open(meta["frame_path"], "rb") as f:
            img_bytes = f.read()
        contents.append(f"Frame at {meta['timestamp']}:")
        contents.append(
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        )

    try:
        response = client.models.generate_content(
            model=config.VISION_MODEL,
            contents=contents,
        )
        return response.text
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "resource_exhausted" in err_msg or "503" in err_msg or "unavailable" in err_msg:
            print(f"Cloud API limit reached. Falling back to local model for answering.")
            return answer_question_local(question, retrieved_metadatas)
        raise e

def answer_question_local(question: str, retrieved_metadatas: list[dict]) -> str:
    """Ask Ollama (Moondream) to answer question using retrieved frames with timestamps."""
    import ollama, base64
    
    # Construct a combined prompt for local model
    images = []
    frame_context = ""
    for meta in retrieved_metadatas:
        with open(meta["frame_path"], "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        images.append(img_b64)
        frame_context += f"- Frame at {meta['timestamp']}\n"
    
    prompt = (
        f"You are looking at several frames from a video at these timestamps:\n{frame_context}\n"
        f"Question: {question}\n"
        "Please answer based on the visual evidence in these frames. Be direct."
    )
    
    # Note: Most local models like Moondream handle 1 image best, 
    # but we can try passing multiple if the Ollama version supports it.
    # Otherwise, we fallback to the most relevant one.
    try:
        response = ollama.chat(
            model=config.OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt, "images": images}]
        )
        return response["message"]["content"]
    except Exception:
        # Fallback to single image if multiple fail
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
    # Peek at first record to see which embedding model was used
    sample = collection.get(limit=1)
    emb_model = "gemini"
    if sample and sample["metadatas"]:
        emb_model = sample["metadatas"][0].get("emb_model", "gemini")

    q_emb = embed_query(client, question, emb_model)
    metas = retrieve_frames(collection, q_emb)
    if not metas:
        return "No relevant frames found."
    
    if config.USE_LOCAL:
        answer = answer_question_local(question, metas)
    else:
        answer = answer_question(client, question, metas)
        
    citations = "\n".join([f"  - {m['timestamp']} ({m['frame_path']})" for m in metas])
    return f"{answer}\n\nSources:\n{citations}"
