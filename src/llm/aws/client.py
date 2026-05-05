"""
AWS client module for SageMaker.
Provides a reusable interface for AWS Bedrock embeddings and LLM calls.
Uses SageMaker-native IAM authentication (no AWS_PROFILE needed).
"""

# Third-party packages
import boto3
from boto3 import Session
from langchain_aws import BedrockEmbeddings, ChatBedrockConverse
from pydantic import BaseModel, PrivateAttr

# Local packages
from logger.config import get_logger

logger = get_logger(__name__)


class AWSClient(BaseModel):
    """Reusable class for AWS Bedrock embeddings and LLM access.

    On SageMaker, boto3 automatically uses the execution role for
    authentication, so no AWS_PROFILE is needed.

    Example:
        client = AWSClient(region="eu-west-1")
        embeddings = client.embeddings_client(
            model_id="cohere.embed-v4:0",
        )

        llm = client.llm_client(
            model_id="eu.anthropic.claude-3-haiku-20240307-v1:0",
            temperature=0.7,
            max_tokens=2000,
        )
    """
    region: str

    _boto_session: Session | None = PrivateAttr(default=None)

    @property
    def session(self) -> Session:
        """Return a boto3 session using SageMaker execution role.

        On SageMaker, credentials are automatically provided via the
        instance metadata service. No profile configuration needed.

        Returns:
            A ``boto3.Session`` bound to the configured region.
        """
        if self._boto_session is not None:
            return self._boto_session

        region = self.region

        self._boto_session = boto3.Session(region_name=region)
        
        logger.info("AWS session created (region=%s)", region)
        
        return self._boto_session

    def refresh_session(self) -> None:
        """Clear cached session and clients so they are re-created
        with fresh credentials on next access.

        Useful when a long-running batch process encounters an
        ``ExpiredTokenException`` from AWS STS.
        """
        self._boto_session = None

        logger.info(
            "AWS session cleared — will re-authenticate on next call"
        )

    def embeddings_client(self, *, model_id: str) -> BedrockEmbeddings:
        """Return a lazily-initialised BedrockEmbeddings client.

        Args:
            model_id: The model id to use.
        """

        bedrock = self.session.client("bedrock-runtime")

        return BedrockEmbeddings(
            client=bedrock,
            model_id=model_id,
        )

    def llm_client(
        self, *,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatBedrockConverse:
        """Return a lazily-initialised ChatBedrockConverse client.

        Args:
            model_id: The model id to use.
            temperature: The temperature to use.
            max_tokens: The max tokens to use.
        """
        bedrock = self.session.client("bedrock-runtime")
        
        return ChatBedrockConverse(
            client=bedrock,
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )
