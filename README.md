# Fintech Knowledge Assistant POC

Local-first RAG stack using FastAPI, Ollama (deepseek-r1:7b + nomic-embed-text), and ChromaDB with a React chat UI.

## Layout
- `backend/` – FastAPI API, RAG pipeline, ingestion script.
- `backend/data/raw/` – Place SOPs, policies, FAQs, test cases here (`.txt`/`.md`).
- `frontend/` – React + Vite chat interface.

## Prereqs
- Python 3.10+
- Node 18+
- Ollama running locally with models:
  ```bash
  ollama pull deepseek-r1:7b
  ollama pull nomic-embed-text
  ```

## Backend setup
```bash
cd /Users/pulkit.jain8004/Documents/FinTech\ POC/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ingest documents:
```bash
python ingest.py
```

Run API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend setup
```bash
cd /Users/pulkit.jain8004/Documents/FinTech\ POC/frontend
npm install
npm run dev
```

Optional: set backend URL in `frontend/.env` as `VITE_API_URL=http://localhost:8000`.


