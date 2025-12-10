import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import get_settings
from app.rag.generator import generate_llm_answer
from app.rag.pipeline import RagPipeline


settings = get_settings()
app = FastAPI(title="Fintech Knowledge Assistant", version="0.1.0")

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Create a pipeline instance for local use in the POST /query path
_pipeline = RagPipeline()


@app.get("/health")
async def health():
    return {"status": "ok", "llm_model": settings.llm_model, "embed_model": settings.embed_model}


# heuristic keyword lists
_GREETINGS = {"hi", "hello", "hey", "hey there", "good morning", "good evening"}
_KB_KEYWORDS = {
    "policy", "sop", "faq", "procedure", "process", "compliance", "onboarding",
    "account", "reset password", "password", "kyc", "sop", "test case", "terms",
    "how to", "how do i", "what is", "step", "steps", "document", "manual"
}

def _contains_kb_keyword(text: str) -> bool:
    t = text.lower()
    for kw in _KB_KEYWORDS:
        if kw in t:
            return True
    return False

def is_rag_query(text: str) -> bool:
    """Return True when query likely needs knowledgebase retrieval."""
    if not text:
        return False
    t = text.strip().lower()
    # short casual greetings -> not RAG
    if t in _GREETINGS or len(t.split()) <= 2 and any(g in t for g in _GREETINGS):
        return False
    # explicit KB keywords
    if _contains_kb_keyword(t):
        return True
    # longer queries that look like factual questions -> RAG
    if len(t.split()) >= 6 and re.search(r"\b(how|what|when|where|why|which|is|are|do|does)\b", t):
        return True
    # default: treat as conversational -> not RAG
    return False


async def call_existing_rag_pipeline(query: str) -> dict:
    """Run the existing RagPipeline and return its result.

    This wraps the synchronous pipeline.run so it can be awaited from FastAPI.
    """
    # pipeline.run is synchronous in this project, call it directly
    result = _pipeline.run(query)
    return result


async def call_existing_llm_answer(query: str) -> dict:
    """Call the permissive LLM-only generator and return a dict with sources=[]"""
    answer = generate_llm_answer(query)
    return {"answer": answer, "sources": []}


@app.post("/query")
async def query_endpoint(payload: dict):
    query_text = (payload.get("query") or "").strip()
    if not query_text:
        return {"answer": "Please provide a question.", "sources": []}

    # decide whether to use RAG or LLM-only
    if not is_rag_query(query_text):
        # direct LLM answer for greetings/general chit-chat
        return await call_existing_llm_answer(query_text)

    # otherwise run the existing RAG pipeline
    return await call_existing_rag_pipeline(query_text)


