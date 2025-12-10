# Backend (FastAPI + RAG)

## Setup
```bash
cd /Users/pulkit.jain8004/Documents/FinTech\ POC/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` if needed (values already default):
```
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=deepseek-r1:7b
EMBED_MODEL=nomic-embed-text
CHROMA_DIR=./data/chroma
COLLECTION_NAME=fintech_docs
TOP_K=5
RERANK_TOP_K=3
MAX_CONTEXT_CHARS=2400
```

## Ingest documents
Place source files in `./data/raw/` (e.g., SOPs, policies, FAQs, test cases as `.txt` or `.md`) then run:
```bash
python ingest.py
```

## Run API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /health`
- `GET /query?q=...`


