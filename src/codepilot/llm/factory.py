"""Builds a LangChain chat model based on configured settings."""

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama


from codepilot.config.settings import get_settings

def get_chat_model(role: str = "fast") -> BaseChatModel:
    """Return a chat model based on the specified role."""
    settings  = get_settings()
    model_name = settings.llm_model_fast if role == "fast" else settings.llm_model_deep

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=model_name,
            base_url=settings.llm_base_url,
            temperature=settings.llm_temperature,
        )
    raise NotImplementedError(f"Unsupported LLM provider: {settings.llm_provider} not wired up ")

