"""
OpenAI client module.
Provides a reusable interface for OpenAI embeddings and LLM calls.
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel

from logger.config import get_logger

logger = get_logger(__name__)


class OpenAIClient(BaseModel):
    """Reusable class for OpenAI embeddings and LLM access.

    Expects the OPENAI_API_KEY to be available via environment variables
    or explicitly passed.

    Example:
        client = OpenAIClient()
        embeddings = client.embeddings_client(
            model_id="text-embedding-3-small",
        )

        llm = client.llm_client(
            model_id="gpt-4o",
            temperature=0.7,
            max_tokens=2000,
        )
    """

    api_key: str | None = None

    def embeddings_client(self, *, model_id: str) -> OpenAIEmbeddings:
        """Return a lazily-initialised OpenAIEmbeddings client.

        Args:
            model_id: The model id to use.
        """
        logger.info("Initializing OpenAIEmbeddings (model_id=%s)", model_id)
        
        return OpenAIEmbeddings(
            model=model_id,
            api_key=self.api_key,
        )

    def llm_client(
        self, *,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatOpenAI:
        """Return a lazily-initialised ChatOpenAI client.

        Args:
            model_id: The model id to use.
            temperature: The temperature to use.
            max_tokens: The max tokens to use.
        """
        logger.info("Initializing ChatOpenAI (model_id=%s)", model_id)
        
        return ChatOpenAI(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.api_key,
        )
