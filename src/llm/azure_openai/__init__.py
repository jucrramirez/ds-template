"""Azure OpenAI provider — available only when ``langchain-openai`` is installed."""

try:
    from llm.azure_openai.client import AzureOpenAIClient

    __all__ = ["AzureOpenAIClient"]
except ImportError:
    __all__ = []
