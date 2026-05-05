"""
Logging configuration module.
Provides a factory function for consistently configured loggers.
"""

import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Return a logger with a pre-configured StreamHandler and optional FileHandler.

    If the logger already has handlers (e.g. after an
    ``%autoreload``), no duplicate handler is added.

    Args:
        name: Logger name, typically ``__name__``.
        level: Logging level (default ``INFO``).
        log_file: Optional path to a file where logs should be saved.

    Returns:
        Configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)
        
        # Always output to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
        # Optionally output to file
        if log_file:
            path = Path(log_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    logger.setLevel(level)
    return logger
