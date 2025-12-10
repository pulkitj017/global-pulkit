"""
Document ingestion for Fintech Knowledge Assistant.

Loads PDF, DOCX, and TXT files from ./data/raw using langchain loaders,
chunks text with RecursiveCharacterTextSplitter, embeds via OllamaEmbeddings
(nomic-embed-text), and persists to ChromaDB.
"""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    DirectoryLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings


settings = get_settings()
RAW_DATA_DIR = Path("./data/raw")


def load_documents() -> List:
    """Load PDF, DOCX, and TXT files via DirectoryLoader."""
    loaders = [
        DirectoryLoader(str(RAW_DATA_DIR), glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(str(RAW_DATA_DIR), glob="**/*.docx", loader_cls=Docx2txtLoader),
        DirectoryLoader(str(RAW_DATA_DIR), glob="**/*.txt", loader_cls=TextLoader),
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    return docs


def split_documents(documents: List) -> List:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_documents(documents)


def ingest() -> None:
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"Raw data folder not found at {RAW_DATA_DIR}")

    docs = load_documents()
    if not docs:
        raise RuntimeError("No documents found (expected PDF/DOCX/TXT in ./data/raw).")

    print(f"Loaded {len(docs)} documents. Splitting...")
    splits = split_documents(docs)
    print(f"Created {len(splits)} chunks. Embedding and storing in Chroma...")

    os.makedirs(settings.chroma_dir, exist_ok=True)

    embeddings = OllamaEmbeddings(model=settings.embed_model)
    Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=settings.collection_name,
        persist_directory=str(settings.chroma_dir),
    )

    print(f"Ingestion complete. Chroma persisted to {settings.chroma_dir}")


if __name__ == "__main__":
    ingest()


