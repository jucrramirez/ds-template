"""Progress bar utilities backed by tqdm."""

from typing import Any

from tqdm.auto import tqdm

_BAR_FORMAT = (
    "{l_bar}{bar}| {n_fmt}/{total_fmt}"
    " [{elapsed}<{remaining}, {rate_fmt}] {postfix}"
)


def get_progress_bar(
    total: int,
    desc: str = "Processing",
    unit: str = "batch",
    **kwargs: Any,
) -> tqdm:
    """Create a tqdm progress bar with consistent formatting.

    Args:
        total: Total number of iterations expected.
        desc: Description prefix for the progress bar.
        unit: String that will be used to define the unit of each iteration.
        **kwargs: Additional keyword arguments passed directly to ``tqdm``.

    Returns:
        A ``tqdm`` progress bar instance.

    Example:
        >>> bar = get_progress_bar(total=100)
        >>> for i in range(100):
        ...     bar.update(1)
    """
    return tqdm(
        total=total,
        desc=desc,
        unit=unit,
        bar_format=_BAR_FORMAT,
        **kwargs,
    )
