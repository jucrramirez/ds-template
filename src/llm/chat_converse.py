"""Generic LLM caller module.

Provides a reusable interface for running LangChain chains
with Langfuse prompts and Bedrock-backed structured output.
"""

from typing import Any

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from pydantic import BaseModel, ConfigDict, PrivateAttr

from llm.protocols import LLMClientProvider
from logger.config import get_logger

logger = get_logger(__name__)


class LLMCaller(BaseModel):
    """Generic LLM caller with structured-output support.

    Combines an ``LLMClientProvider`` with model configuration, prompt, and schema
    to act as a stateful, reusable pipeline.

    Example:
        caller = LLMCaller(
            client_provider=AWSClient(region="eu-west-1"),
            prompt_template=PromptTemplate.from_template("Summarise: {text}"),
            schema=MySummarySchema,
            model_id="eu.anthropic.claude-3-haiku-20240307-v1:0",
            temperature=0.0,
            max_tokens=1000,
        )
        result = caller.invoke(input_variables={"text": "Long document..."})
        results = caller.batch_invoke(inputs=[{"text": "Doc 1"}, {"text": "Doc 2"}])
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    client_provider: LLMClientProvider
    prompt_template: PromptTemplate
    schema: type[BaseModel]
    model_id: str
    temperature: float
    max_tokens: int

    _chain: Runnable | None = PrivateAttr(default=None)

    @property
    def chain(self) -> Runnable:
        """Lazily build and return the LangChain chain."""
        if self._chain is None:
            structured_llm = self.client_provider.llm_client(
                model_id=self.model_id,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            ).with_structured_output(self.schema)
            self._chain = self.prompt_template | structured_llm
        return self._chain

    def invoke(self, input_variables: dict[str, Any]) -> BaseModel:
        """Invoke the structured-output chain.

        Args:
            input_variables: Placeholder values injected into the prompt template.

        Returns:
            An instance of ``schema`` populated by the LLM.
        """
        return self.chain.invoke(input_variables)

    def batch_invoke(
        self,
        inputs: list[dict[str, Any]],
        *,
        max_concurrency: int = 5,
        return_exceptions: bool = True,
    ) -> list:
        """Invoke the chain on multiple inputs concurrently.

        Wraps LangChain's ``Runnable.batch()`` which uses a
        ``ThreadPoolExecutor`` internally.

        Args:
            inputs: List of input dicts, one per invocation.
            max_concurrency: Maximum parallel threads hitting the LLM simultaneously.
            return_exceptions: If ``True``, failed items return their exception instead of raising.

        Returns:
            A list of outputs (or exceptions when ``return_exceptions=True``), one per input.
        """
        return self.chain.batch(
            inputs,
            config={"max_concurrency": max_concurrency},
            return_exceptions=return_exceptions,
        )
