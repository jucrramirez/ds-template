"""
Configuration loader module.
Provides centralized access to pipeline configuration from YAML files.

Two typical entry points:

- **Default pipeline:** ``load_config()`` or ``load_config(None)`` discovers
  ``config/pipeline_config.yaml`` upward from this package.
- **Exploratory / alternate same-shape file:** pass an explicit path such as
  ``load_config("config/exploratory_config.yaml")`` (or an absolute path).

Both modes parse into the same :class:`Config` model.
"""

# Built-in packages
from pathlib import Path
from typing import Any

# Third-party packages
import yaml

# Local packages
from config.schemas import Config

_config: Config | None = None
_resolved_config_path: Path | None = None

def _find_config_path(
    filename: str = "pipeline_config.yaml",
) -> Path:
    """Locate a config file inside the ``config/`` directory.

    Walks up from this module's location until it finds a parent that contains
    ``config/<filename>``.

    Args:
        filename: Basename of the YAML file (e.g. ``pipeline_config.yaml``).

    Returns:
        Absolute path to the file.

    Raises:
        FileNotFoundError: If no matching file exists in any parent.
    """
    current = Path(__file__).resolve()

    for parent in current.parents:
        candidate = parent / "config" / filename
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find config/{filename} in any parent directory"
    )


def _resolve_load_path(config_path: str | Path | None) -> Path:
    """Resolve *config_path* to an absolute filesystem path."""
    if config_path is None:
        return _find_config_path()
    resolved = Path(config_path)
    if resolved.is_absolute():
        if not resolved.exists():
            raise FileNotFoundError(f"Config file not found: {resolved}")
        return resolved.resolve()
    if resolved.exists():
        return resolved.resolve()
    filename = resolved.name
    return _find_config_path(filename)


def load_config(config_path: str | Path | None = None) -> Config:
    """Load and parse a pipeline-style YAML file into :class:`Config`.

    **Caching:** A successful load stores the result. Calling
    ``load_config(None)`` returns the cached instance without re-reading disk
    when a cache exists. Passing a **non-**``None`` *config_path* always loads
    from disk and **replaces** the cache (e.g. switch to exploratory settings
    in the same process).

    Args:
        config_path: Where to load from:

            - ``None`` — use cached config if present; otherwise discover
              ``config/pipeline_config.yaml``.
            - Relative path that does not exist as given — treated as a basename
              and resolved via :func:`_find_config_path` (e.g.
              ``"exploratory_config.yaml"``).
            - Path that exists — loaded directly (relative paths resolved from
              cwd).

    Returns:
        Parsed and validated :class:`Config`.

    Raises:
        FileNotFoundError: If the YAML file cannot be found.
        ValidationError: If the file does not match the model.

    Example:
        Default discovery::

            cfg = load_config()

        Explicit exploratory file (same schema as pipeline)::

            cfg = load_config("config/exploratory_config.yaml")
    """
    global _config, _resolved_config_path

    if config_path is None and _config is not None:
        return _config

    resolved = _resolve_load_path(config_path)

    with open(resolved, encoding="utf-8") as f:
        raw_config: dict[str, Any] = yaml.safe_load(f)

    _config = Config(**raw_config)
    _resolved_config_path = resolved
    return _config


def reset_config() -> None:
    """Clear the cached configuration and resolved path.

    Use before ``load_config(None)`` when you need to force a fresh read of
    the default ``pipeline_config.yaml`` after loading another file, or in
    tests for isolation.

    Example:
        After exploratory work, reload defaults::

            reset_config()
            load_config()
    """
    global _config, _resolved_config_path
    _config = None
    _resolved_config_path = None


def get_config() -> Config:
    """Return the cached configuration, loading default YAML if needed.

    Returns:
        The current :class:`Config` (same instance as last
        :func:`load_config` until :func:`reset_config`).

    Example:
        >>> cfg = get_config()  # doctest: +SKIP
        >>> cfg.aws.region  # doctest: +SKIP
        'eu-west-1'
    """
    if _config is None:
        return load_config()
    return _config


def get_storage_path(storage_type: str) -> Path:
    """Return an absolute path under the project root for a storage bucket.

    The project root is inferred from the **last successfully loaded** config
    file (``<project>/config/<file>.yaml`` → ``<project>``), not from a fixed
    default filename.

    Args:
        storage_type: One of ``\"datasets\"``, ``\"tmp\"``, or ``\"exports\"``
            (keys of :attr:`PipelineConfig.storage`).

    Returns:
        Absolute directory path (may not exist yet).

    Raises:
        ValueError: If *storage_type* is not recognized.
        RuntimeError: If no config has been loaded yet (call
            :func:`load_config` first).

    Example:
        >>> load_config()  # doctest: +SKIP
        >>> p = get_storage_path("tmp")  # doctest: +SKIP
        >>> p.name == "tmp"  # doctest: +SKIP
        True
    """
    config = get_config()
    if _resolved_config_path is None:
        raise RuntimeError(
            "Storage path requires a loaded config with a resolved file path; "
            "call load_config() first."
        )
    project_root = _resolved_config_path.resolve().parent.parent

    storage_map = {
        "datasets": config.storage.datasets,
        "tmp": config.storage.tmp,
        "exports": config.storage.exports,
    }

    if storage_type not in storage_map:
        raise ValueError(f"Unknown storage type: {storage_type}")

    return project_root / storage_map[storage_type]
