"""OpenAI provider — available only when ``langchain-openai`` is installed."""

try:
    from llm.openai.client import OpenAIClient

    __all__ = ["OpenAIClient"]
except ImportError:
    __all__ = []
