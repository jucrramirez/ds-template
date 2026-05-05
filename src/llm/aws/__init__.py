"""AWS provider — available only when ``langchain-aws`` and ``boto3`` are installed."""

try:
    from llm.aws.client import AWSClient

    __all__ = ["AWSClient"]
except ImportError:
    __all__ = []
