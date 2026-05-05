"""CSV serializer for Polars DataFrames."""

from pathlib import Path

import polars as pl

from logger.config import get_logger

logger = get_logger(__name__)


class CsvHandler:
    """Read and write Polars DataFrames as CSV files.

    Example:
        CsvHandler.save(df, "data/output.csv")
        df = CsvHandler.load("data/output.csv")
    """

    @staticmethod
    def save(data: pl.DataFrame, filepath: str | Path) -> None:
        """Write a DataFrame to a CSV file.

        Args:
            data: Polars DataFrame to persist.
            filepath: Destination path (directories are
                created automatically).
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data.write_csv(filepath)
        logger.info("Saved %s rows to %s", len(data), filepath.name)

    @staticmethod
    def load(filepath: str | Path) -> pl.DataFrame:
        """Read a CSV file into a DataFrame.

        Args:
            filepath: Path to the ``.csv`` file.

        Returns:
            Polars DataFrame.
        """
        df = pl.read_csv(filepath)
        logger.info(
            "Loaded %s rows from %s",
            len(df),
            Path(filepath).name,
        )
        return df
