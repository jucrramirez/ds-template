"""
Ollama client module.
Provides a reusable interface for Ollama embeddings and LLM calls.
"""

from langchain_ollama import ChatOllama, OllamaEmbeddings
from pydantic import BaseModel

from logger.config import get_logger

logger = get_logger(__name__)


class OllamaClient(BaseModel):
    """Reusable class for Ollama embeddings and LLM access.

    Expects the Ollama service to be running locally or available at `base_url`.

    Example:
        client = OllamaClient(base_url="http://localhost:11434")
        embeddings = client.embeddings_client(
            model_id="nomic-embed-text",
        )

        llm = client.llm_client(
            model_id="llama3.1",
            temperature=0.0,
            max_tokens=2000,
        )
    """

    base_url: str = "http://localhost:11434"

    def embeddings_client(self, *, model_id: str) -> OllamaEmbeddings:
        """Return a lazily-initialised OllamaEmbeddings client.

        Args:
            model_id: The model id to use.
        """
        logger.info("Initializing OllamaEmbeddings (model_id=%s, base_url=%s)", model_id, self.base_url)
        
        return OllamaEmbeddings(
            model=model_id,
            base_url=self.base_url,
        )

    def llm_client(
        self, *,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatOllama:
        """Return a lazily-initialised ChatOllama client.

        Args:
            model_id: The model id to use.
            temperature: The temperature to use.
            max_tokens: The max tokens to use.
        """
        logger.info("Initializing ChatOllama (model_id=%s, base_url=%s)", model_id, self.base_url)
        
        return ChatOllama(
            model=model_id,
            temperature=temperature,
            num_predict=max_tokens,
            base_url=self.base_url,
        )
