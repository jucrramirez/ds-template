"""Parquet serializer for Polars DataFrames."""

from pathlib import Path

import polars as pl

from logger.config import get_logger

logger = get_logger(__name__)


class ParquetHandler:
    """Read and write Polars DataFrames as Parquet files.

    Example:
        handler = ParquetHandler()
        handler.save(df, "data/output.parquet")
        df = handler.load("data/output.parquet")
    """

    @staticmethod
    def save(data: pl.DataFrame, filepath: str | Path) -> None:
        """Write a DataFrame to a Parquet file.

        Args:
            data: Polars DataFrame to persist.
            filepath: Destination path (directories are
                created automatically).
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data.write_parquet(filepath)
        logger.info("Saved %s rows to %s", len(data), filepath.name)

    @staticmethod
    def load(filepath: str | Path) -> pl.DataFrame:
        """Read a Parquet file into a DataFrame.

        Args:
            filepath: Path to the ``.parquet`` file.

        Returns:
            Polars DataFrame.
        """
        df = pl.read_parquet(filepath)
        logger.info(
            "Loaded %s rows from %s",
            len(df),
            Path(filepath).name,
        )
        return df
