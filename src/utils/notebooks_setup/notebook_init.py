"""
Notebook initialization utilities.
Provides shared setup code for all pipeline notebooks.
"""

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from config.loader import Config, get_storage_path, load_config
from utils.logger.config import get_logger

_logger = get_logger(__name__)


def init_notebook(
    name: str = "__main__",
    config_path: str | Path | None = None,
) -> tuple[Config, Any]:
    """Standard notebook initialization.

    Performs common setup tasks:

    - Loads environment variables from ``.env``
    - Loads pipeline configuration via :func:`config.loader.load_config`
    - Creates a logger instance

    A non-``None`` *config_path* replaces the process-wide config cache (same
    semantics as :func:`config.loader.load_config`). To force a fresh default
    pipeline file after loading another YAML, call
    :func:`config.loader.reset_config` before ``init_notebook(..., None)``.

    Args:
        name: Logger name (typically ``__name__`` from the notebook).
        config_path: Optional path to a YAML file with the same shape as
            ``config.yaml``. When ``None``, discovers
            ``config/config.yaml`` (or returns the cached config).

    Returns:
        Tuple ``(config, logger)`` for use in the notebook.

    Example:
        Default pipeline config::

            config, logger = init_notebook(__name__)

        Exploratory config (gitignored locally; same schema as pipeline)::

            config, logger = init_notebook(
                __name__,
                config_path="config/exploratory_config.yaml",
            )
    """
    load_dotenv()
    config = load_config(config_path)
    logger = get_logger(name)

    # Ensure storage paths exist automatically
    ensure_storage_dirs()

    return config, logger


def ensure_storage_dirs() -> dict[str, Path]:
    """Ensure all configured storage directories exist under the project root.

    Uses :func:`config.loader.get_storage_path` for each of ``datasets``,
    ``tmp``, and ``exports``.

    Returns:
        Mapping from storage type string to absolute :class:`~pathlib.Path`.

    Example:
        >>> # ensure_storage_dirs()  # doctest: +SKIP
        >>> # {"datasets": Path(".../files/datasets"), ...}  # doctest: +SKIP
    """
    storage_types = ["datasets", "tmp", "exports"]
    paths = {}

    for storage_type in storage_types:
        path = get_storage_path(storage_type)
        path.mkdir(parents=True, exist_ok=True)
        paths[storage_type] = path

    return paths
