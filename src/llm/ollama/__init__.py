"""Ollama provider — available only when ``langchain-ollama`` is installed."""

try:
    from llm.ollama.client import OllamaClient

    __all__ = ["OllamaClient"]
except ImportError:
    __all__ = []
