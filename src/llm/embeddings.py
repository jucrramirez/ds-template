"""Generic embeddings caller module.

Provides a reusable interface for generating embeddings
using a generic LLM client provider.
"""

from pydantic import BaseModel, ConfigDict

from llm.protocols import LLMClientProvider
from utils.logger.config import get_logger

logger = get_logger(__name__)


class EmbeddingsCaller(BaseModel):
    """Generic Embeddings caller.

    Uses an ``LLMClientProvider`` to build an embeddings client
    and generate embeddings for lists of texts.

    Example:
        caller = EmbeddingsCaller(client_provider=AWSClient(region="eu-west-1"))
        vectors = caller.embed_documents(
            texts=["Hello world", "Goodbye world"],
            model_id="cohere.embed-v4:0",
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client_provider: LLMClientProvider

    def embed_documents(
        self,
        *,
        texts: list[str],
        model_id: str,
    ) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            texts: List of strings to embed.
            model_id: The model ID to use for the provider.

        Returns:
            A list of vector embeddings (lists of floats).
        """
        logger.info("Embedding %d documents using model_id=%s", len(texts), model_id)
        client = self.client_provider.embeddings_client(model_id=model_id)
        return client.embed_documents(texts)

    def embed_query(
        self,
        *,
        text: str,
        model_id: str,
    ) -> list[float]:
        """Embed a single query.

        Args:
            text: String to embed.
            model_id: The model ID to use for the provider.

        Returns:
            A single vector embedding (list of floats).
        """
        logger.info("Embedding query using model_id=%s", model_id)
        client = self.client_provider.embeddings_client(model_id=model_id)
        return client.embed_query(text)
