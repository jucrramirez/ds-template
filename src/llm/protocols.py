"""Protocols for LLM providers."""

from typing import Protocol, runtime_checkable

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel


@runtime_checkable
class LLMClientProvider(Protocol):
    """Protocol defining the required methods for an LLM client provider."""

    def llm_client(
        self, *, model_id: str, temperature: float, max_tokens: int
    ) -> BaseChatModel:
        """Return an initialized LLM client."""
        ...

    def embeddings_client(self, *, model_id: str) -> Embeddings:
        """Return an initialized Embeddings client."""
        ...
