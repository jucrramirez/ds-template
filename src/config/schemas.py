"""
Definition of the schemas for the configuration loader.
"""

# Built-in packages
from pathlib import Path

# Third-party packages
from pydantic import BaseModel


class StorageConfig(BaseModel):
    """Storage paths configuration (relative to project root)."""

    datasets: str
    tmp: str
    exports: str


class BatchConfig(BaseModel):
    """Batch processing configuration."""

    max_retries: int
    retry_delay: float
    save_frequency: int


class LLMConfig(BaseModel):
    """Generic LLM parameters."""

    temperature: float
    max_tokens: int
    max_concurrency: int
    batch_size: int


class EmbeddingsConfig(BaseModel):
    """Embeddings configuration."""

    batch_size: int
    input_type: str
    output_dimension: int
    embedding_types: list[str]
    truncate: str
    max_tokens: int


class Config(BaseModel):
    """Root configuration model (shared by the config YAML).
    
    Add domain-specific configuration models (like DatabaseConfig) here
    as you expand the project.

    Example:
        >>> config = Config(
        ...     storage=StorageConfig(datasets="...", tmp="...", exports="..."),
        ...     batch=BatchConfig(max_retries=3, retry_delay=1.0, save_frequency=10),
        ...     llm=LLMConfig(temperature=0.0, max_tokens=1000, max_concurrency=5, batch_size=10),
        ...     embeddings=EmbeddingsConfig(batch_size=100, input_type="...", output_dimension=768, embedding_types=["..."], truncate="...", max_tokens=8192)
        ... )
    """

    storage: StorageConfig
    batch: BatchConfig
    llm: LLMConfig
    embeddings: EmbeddingsConfig
