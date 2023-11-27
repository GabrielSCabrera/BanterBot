import time
from dataclasses import dataclass
from typing import Any, Optional

from banterbot.utils.time_resolver import TimeResolver


@dataclass
class StreamLogEntry:
    """
    A dataclass used for storage of data that is yielded from a data stream in class `StreamHandler`.
    """

    value: Any
    timestamp: Optional[int] = None

    def __post_init__(self) -> None:
        """
        Record the time at which the entry was logged using `perf_counter_ns()`.
        """
        self.timestamp = time.perf_counter_ns()

    def __str__(self) -> str:
        """
        Return metadata about the entry.

        Returns:
            str: Metadata about the current entry.
        """
        return f"<StreamLogEntry at {TimeResolver.resolve(self.timestamp)} of type `{type(self.value)}`>"

    def __repr__(self) -> str:
        """
        Return metadata about the entry in a more compact form.

        Returns:
            str: Metadata about the current entry.
        """
        return f"<StreamLogEntry | {self.timestamp} | {type(self.value)}>"
