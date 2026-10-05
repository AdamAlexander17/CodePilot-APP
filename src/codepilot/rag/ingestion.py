"""Walks a repository, chunks its files, and stores embeddings in its vector store."""

from codepilot.security.secret_redaction import is_blocked_filename, redact_secrets

from pathlib import Path

from langchain_core.documents import Document

from codepilot.rag.chunking import chunk_text
from codepilot.rag.vector_store import get_vector_store

IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
TEXT_EXTENSIONS = {".py", ".js", ".ts", ".md", ".txt", ".json", ".yaml", ".yml", ".html", ".css"}


def ingest_repository(repo_path: str) -> int:
    """Ingest every text file in the repo. Returns the number of chunks stored."""
    root = Path(repo_path).resolve()
    store = get_vector_store(repo_path)

    documents = []
    for file_path in root.rglob("*"):
        if not file_path.is_file() or IGNORED_DIRS.intersection(file_path.parts):
            continue
        if file_path.suffix not in TEXT_EXTENSIONS:
            continue
        if is_blocked_filename(file_path.name):
            continue

        content = file_path.read_text(encoding="utf-8", errors="replace")
        content = redact_secrets(content)
        relative_path = str(file_path.relative_to(root))

        for chunk in chunk_text(content):
            documents.append(Document(page_content=chunk, metadata={"source": relative_path}))

    if documents:
        store.add_documents(documents)

    return len(documents)
