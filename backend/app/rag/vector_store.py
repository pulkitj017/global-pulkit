from typing import Optional, Sequence

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models import Collection
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.rag.embeddings import embed_texts


settings = get_settings()


def get_chroma_client() -> ClientAPI:
    # Persistent client so we see the same data as ingestion
    return chromadb.PersistentClient(
        path=str(settings.chroma_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_collection(client: Optional[ClientAPI] = None) -> Collection:
    client = client or get_chroma_client()
    return client.get_or_create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,  # We handle embeddings ourselves
    )


def add_documents(
    texts: Sequence[str],
    metadatas: Sequence[dict],
    ids: Sequence[str],
    collection: Optional[Collection] = None,
) -> None:
    collection = collection or get_collection()
    embeddings = embed_texts(list(texts))
    collection.add(
        documents=list(texts),
        metadatas=list(metadatas),
        ids=list(ids),
        embeddings=embeddings,
    )
    # Persist to disk
    collection.persist()


def query_collection(
    query_text: str,
    top_k: int,
    collection: Optional[Collection] = None,
) -> dict:
    collection = collection or get_collection()
    query_embedding = embed_texts([query_text])[0]
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "embeddings"],
    )


