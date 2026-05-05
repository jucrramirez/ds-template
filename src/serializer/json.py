"""JSON serializer for Python objects."""

import json
from pathlib import Path
from typing import Any


class JsonHandler:
    """Read and write Python objects as JSON files.

    Example:
        handler = JsonHandler()
        handler.save({"key": "value"}, "data/output.json")
        obj = handler.load("data/output.json")
    """

    @staticmethod
    def save(
        data: Any,
        filepath: str | Path,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> None:
        """Serialise an object to a JSON file.

        Args:
            data: JSON-serialisable object.
            filepath: Destination path (directories are
                created automatically).
            indent: JSON indentation level.
            ensure_ascii: If ``False``, allow non-ASCII
                characters in the output.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open("w", encoding="utf-8") as fh:
            json.dump(
                data,
                fh,
                indent=indent,
                ensure_ascii=ensure_ascii,
            )

    @staticmethod
    def load(filepath: str | Path) -> Any:
        """Deserialise a JSON file into a Python object.

        Args:
            filepath: Path to the ``.json`` file.

        Returns:
            Deserialised Python object.
        """
        with Path(filepath).open(encoding="utf-8") as fh:
            return json.load(fh)
