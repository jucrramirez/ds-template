"""
Gemini client module.
Provides a reusable interface for Google Gemini embeddings and LLM calls.
"""

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pydantic import BaseModel

from utils.logger.config import get_logger

logger = get_logger(__name__)


class GeminiClient(BaseModel):
    """Reusable class for Google Gemini embeddings and LLM access.

    Expects the Google API key to be available via environment variables
    (e.g., GOOGLE_API_KEY) or explicitly passed.

    Example:
        client = GeminiClient()
        embeddings = client.embeddings_client(
            model_id="models/text-embedding-004",
        )

        llm = client.llm_client(
            model_id="gemini-1.5-pro",
            temperature=0.7,
            max_tokens=2000,
        )
    """

    api_key: str | None = None

    def embeddings_client(self, *, model_id: str) -> GoogleGenerativeAIEmbeddings:
        """Return a lazily-initialised GoogleGenerativeAIEmbeddings client.

        Args:
            model_id: The model id to use.
        """
        logger.info("Initializing GoogleGenerativeAIEmbeddings (model_id=%s)", model_id)
        
        return GoogleGenerativeAIEmbeddings(
            model=model_id,
            google_api_key=self.api_key,
        )

    def llm_client(
        self, *,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatGoogleGenerativeAI:
        """Return a lazily-initialised ChatGoogleGenerativeAI client.

        Args:
            model_id: The model id to use.
            temperature: The temperature to use.
            max_tokens: The max tokens to use.
        """
        logger.info("Initializing ChatGoogleGenerativeAI (model_id=%s)", model_id)
        
        return ChatGoogleGenerativeAI(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            google_api_key=self.api_key,
        )
