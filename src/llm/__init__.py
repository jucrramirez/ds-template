"""LLM package.

Exposes provider clients and the generic pipeline classes.
Each provider is imported conditionally — if its optional dependency is not
installed the class is simply not available, instead of raising an ImportError
at package load time.

Available providers (require separate installation):
    - AWSClient        → ``langchain-aws boto3``
    - GeminiClient     → ``langchain-google-genai``
    - OpenAIClient     → ``langchain-openai``
    - AzureOpenAIClient → ``langchain-openai``
    - OllamaClient     → ``langchain-ollama``

Core pipeline classes are always available (require only ``langchain-core``
and ``pydantic``):
    - LLMCaller
    - EmbeddingsCaller
    - LLMClientProvider
"""

from llm.chat_converse import LLMCaller
from llm.embeddings import EmbeddingsCaller
from llm.protocols import LLMClientProvider

__all__: list[str] = [
    "LLMCaller",
    "EmbeddingsCaller",
    "LLMClientProvider",
]

# --- Optional provider imports ------------------------------------------------

try:
    from llm.aws.client import AWSClient

    __all__.append("AWSClient")
except ImportError:
    pass

try:
    from llm.gemini.client import GeminiClient

    __all__.append("GeminiClient")
except ImportError:
    pass

try:
    from llm.openai.client import OpenAIClient

    __all__.append("OpenAIClient")
except ImportError:
    pass

try:
    from llm.azure_openai.client import AzureOpenAIClient

    __all__.append("AzureOpenAIClient")
except ImportError:
    pass

try:
    from llm.ollama.client import OllamaClient

    __all__.append("OllamaClient")
except ImportError:
    pass
