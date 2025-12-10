from typing import List, Tuple

from app.rag.embeddings import cosine_similarity, embed_text


def rerank(query: str, docs: List[Tuple[str, dict, list]], top_k: int) -> List[Tuple[str, dict, list, float]]:
    """
    Re-rank documents using cosine similarity on fresh query embedding vs doc embeddings.
    docs: list of tuples (document, metadata, embedding)
    Returns list of tuples (document, metadata, embedding, score) sorted desc by score.
    """
    if not docs:
        return []
    query_embedding = embed_text(query)
    scored = []
    for doc, meta, embedding in docs:
        score = cosine_similarity(query_embedding, embedding)
        scored.append((doc, meta, embedding, score))
    scored.sort(key=lambda x: x[3], reverse=True)
    return scored[:top_k]


