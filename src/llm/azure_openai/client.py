"""
Azure OpenAI client module.
Provides a reusable interface for Azure OpenAI embeddings and LLM calls.
"""

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import BaseModel

from utils.logger.config import get_logger

logger = get_logger(__name__)


class AzureOpenAIClient(BaseModel):
    """Reusable class for Azure OpenAI embeddings and LLM access.

    Expects standard Azure environment variables (AZURE_OPENAI_API_KEY, 
    AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION) to be set or explicitly passed.

    Example:
        client = AzureOpenAIClient(
            api_version="2024-02-01",
            azure_endpoint="https://my-resource.openai.azure.com/"
        )
        embeddings = client.embeddings_client(
            model_id="text-embedding-3-small-deployment",
        )

        llm = client.llm_client(
            model_id="gpt-4o-deployment",
            temperature=0.7,
            max_tokens=2000,
        )
    """

    api_key: str | None = None
    azure_endpoint: str | None = None
    api_version: str | None = None

    def embeddings_client(self, *, model_id: str) -> AzureOpenAIEmbeddings:
        """Return a lazily-initialised AzureOpenAIEmbeddings client.

        Args:
            model_id: The deployment name to use in Azure.
        """
        logger.info("Initializing AzureOpenAIEmbeddings (azure_deployment=%s)", model_id)
        
        return AzureOpenAIEmbeddings(
            azure_deployment=model_id,
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            openai_api_version=self.api_version,
        )

    def llm_client(
        self, *,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> AzureChatOpenAI:
        """Return a lazily-initialised AzureChatOpenAI client.

        Args:
            model_id: The deployment name to use in Azure.
            temperature: The temperature to use.
            max_tokens: The max tokens to use.
        """
        logger.info("Initializing AzureChatOpenAI (azure_deployment=%s)", model_id)
        
        return AzureChatOpenAI(
            azure_deployment=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
        )
