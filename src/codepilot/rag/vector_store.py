"""Builds a per-repository Chroma vector store."""

import hashlib
from pathlib import Path

from langchain_chroma import Chroma

from codepilot.rag.embeddings import get_embeddings

_STORE_ROOT = Path("RAG_-DB/.vector_stores")


def get_vector_store(repo_path: str) -> Chroma:
    repo_hash = hashlib.sha256(repo_path.encode()).hexdigest()[:16]
    persist_dir = _STORE_ROOT / repo_hash
    persist_dir.mkdir(parents=True, exist_ok=True)

    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=get_embeddings(),
    )
