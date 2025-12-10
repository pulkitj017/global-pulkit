from typing import List

import numpy as np
import ollama

from app.config import get_settings


settings = get_settings()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a list of texts using the local Ollama embedding model."""
    if not texts:
        return []
    embeddings: List[List[float]] = []
    for text in texts:
        resp = ollama.embeddings(model=settings.embed_model, prompt=text)
        embeddings.append(resp["embedding"])
    return embeddings


def embed_text(text: str) -> List[float]:
    return embed_texts([text])[0]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a_vec = np.array(a)
    b_vec = np.array(b)
    denom = np.linalg.norm(a_vec) * np.linalg.norm(b_vec)
    if denom == 0:
        return 0.0
    return float(np.dot(a_vec, b_vec) / denom)


