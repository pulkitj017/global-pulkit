import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Base URL for the local Ollama instance",
    )
    llm_model: str = Field(
        default="llama3.1:8b", description="Local LLM model name served by Ollama"
    )
    embed_model: str = Field(
        default="nomic-embed-text",
        description="Embedding model name served by Ollama",
    )
    chroma_dir: Path = Field(
        default=Path("./data/chroma"), description="Persistent storage path for Chroma"
    )
    collection_name: str = Field(
        default="fintech_docs", description="Chroma collection name"
    )
    top_k: int = Field(default=8, description="Number of documents to retrieve")
    rerank_top_k: int = Field(
        default=5, description="Number of documents to keep after re-ranking"
    )
    max_context_chars: int = Field(
        default=2400, description="Max characters from context to feed the LLM"
    )
    # Minimum relevance score required to consider KB evidence valid. If the
    # highest document score is below this threshold, the pipeline will
    # respond with 'Information not available.' instead of falling back to
    # the permissive LLM.
    rag_score_threshold: float = Field(
        default=0.5, description="Minimum cosine similarity to accept KB evidence"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Ensure chroma directory exists early
    settings = Settings()
    os.environ.setdefault("OLLAMA_HOST", str(settings.ollama_host))
    os.makedirs(settings.chroma_dir, exist_ok=True)
    return settings


