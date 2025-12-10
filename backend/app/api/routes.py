from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.rag.pipeline import RagPipeline
from app.rag.generator import generate_llm_answer


router = APIRouter()
pipeline = RagPipeline()


class QueryResponse(BaseModel):
    answer: str
    sources: list


# Lightweight heuristic to decide whether a query should go through RAG or be
# answered directly by the LLM. This mirrors the behaviour we use in
# `app/main.py` but keeps routes self-contained to avoid circular imports.
_GREETINGS = {"hi", "hello", "hey", "hey there", "good morning", "good evening"}
_KB_KEYWORDS = {
    "policy", "sop", "faq", "procedure", "process", "compliance", "onboarding",
    "account", "reset password", "password", "kyc", "test case", "terms",
    "how to", "how do i", "what is", "step", "steps", "document", "manual"
}


def _contains_kb_keyword(text: str) -> bool:
    t = text.lower()
    for kw in _KB_KEYWORDS:
        if kw in t:
            return True
    return False


def is_rag_query(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    if t in _GREETINGS or (len(t.split()) <= 2 and any(g in t for g in _GREETINGS)):
        return False
    if _contains_kb_keyword(t):
        return True
    # default to RAG for longer, fact-like questions
    if len(t.split()) >= 6:
        return True
    return False


@router.get("/query", response_model=QueryResponse)
async def query_documents(q: str = Query(..., min_length=1, description="User question")):
    try:
        # If heuristic says this is not a KB query, use the LLM directly.
        if not is_rag_query(q):
            answer = generate_llm_answer(q)
            return QueryResponse(answer=answer, sources=[])

        # Otherwise run the RAG pipeline as before
        result = pipeline.run(q)
        return QueryResponse(**result)
    except Exception as exc:  # pylint: disable=broad-except
        # Log error in real use; return safe message
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc


