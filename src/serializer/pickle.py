"""Pickle serializer for arbitrary Python objects."""

import pickle
from pathlib import Path
from typing import Any


class PickleHandler:
    """Read and write Python objects as pickle files.

    Example:
        handler = PickleHandler()
        handler.save(my_object, "data/output.pickle")
        obj = handler.load("data/output.pickle")
    """

    @staticmethod
    def save(data: Any, filepath: str | Path) -> None:
        """Persist an object to a pickle file.

        Args:
            data: Any picklable Python object.
            filepath: Destination path (directories are
                created automatically).
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open("wb") as fh:
            pickle.dump(data, fh)

    @staticmethod
    def load(filepath: str | Path) -> Any:
        """Load an object from a pickle file.

        Args:
            filepath: Path to the ``.pickle`` file.

        Returns:
            Deserialised Python object.
        """
        with Path(filepath).open("rb") as fh:
            return pickle.load(fh)  # noqa: S301
