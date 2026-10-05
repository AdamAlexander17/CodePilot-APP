"""Builds the embedding model used to turn text into vectors for RAG."""

from langchain_ollama import OllamaEmbeddings

from codepilot.config.settings import get_settings


def get_embeddings() -> OllamaEmbeddings:
    settings = get_settings()
    return OllamaEmbeddings(model="nomic-embed-text", base_url=settings.llm_base_url)
