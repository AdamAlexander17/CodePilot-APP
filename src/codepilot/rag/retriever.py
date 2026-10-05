"""Semantic search over an ingested repository's embedded chunks."""

from codepilot.rag.vector_store import get_vector_store


def search_similar_chunks(repo_path: str, query: str, k: int = 4) -> list[dict[str, str]]:
    store = get_vector_store(repo_path)
    results = store.similarity_search(query, k=k)
    return [{"source": doc.metadata.get("source", "unknown"), "text": doc.page_content} for doc in results]
