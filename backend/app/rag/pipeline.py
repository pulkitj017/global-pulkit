from typing import Dict, List, Optional, Tuple

from app.config import get_settings
from app.rag.generator import generate_answer
from app.rag.rerank import rerank
from app.rag.vector_store import query_collection


settings = get_settings()


class RagPipeline:
    def __init__(self) -> None:
        self.top_k = settings.top_k
        self.rerank_top_k = settings.rerank_top_k
        self.max_context_chars = settings.max_context_chars

    def _retrieve(self, query: str) -> List[Tuple[str, dict, list]]:
        result = query_collection(query, top_k=self.top_k)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        embeddings = result.get("embeddings", [[]])[0]
        # When collection is empty, Chroma returns empty lists
        combined = list(zip(docs, metas, embeddings))
        return combined

    def _build_contexts(self, docs: List[Tuple[str, dict, list, float]]) -> List[str]:
        contexts: List[str] = []
        running = 0
        for doc, meta, _, score in docs:
            snippet_header = f"[{meta.get('source', 'document')}] (score={score:.2f})\n"
            snippet = snippet_header + doc
            if running + len(snippet) > self.max_context_chars:
                break
            contexts.append(snippet)
            running += len(snippet)
        return contexts

    def run(self, query: str) -> Dict[str, Optional[str]]:
        retrieved = self._retrieve(query)
        reranked = rerank(query, retrieved, self.rerank_top_k)
        contexts = self._build_contexts(reranked)

        # collect scores in the same order as contexts were built
        scores = [score for _, _, __, score in reranked[: len(contexts)]]

        # If no contexts or top score below threshold, return strict fallback
        if not contexts or max(scores, default=0.0) < settings.rag_score_threshold:
            return {
                "answer": "Information not available.",
                "sources": [],
            }

        # pass scores to generator which will produce an evidence-backed answer
        answer = generate_answer(query, contexts, scores)
        # If model refused or returned the fallback string, enforce fallback
        if not answer or "Information not available" in answer:
            return {"answer": "Information not available.", "sources": []}

        # Return only the sources that were included in contexts (preserve scores)
        sources = [
            {"source": meta.get("source"), "score": score}
            for _, meta, __, score in reranked[: len(contexts)]
        ]
        return {"answer": answer, "sources": sources}


