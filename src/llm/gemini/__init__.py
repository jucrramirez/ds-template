"""Gemini provider — available only when ``langchain-google-genai`` is installed."""

try:
    from llm.gemini.client import GeminiClient

    __all__ = ["GeminiClient"]
except ImportError:
    __all__ = []
