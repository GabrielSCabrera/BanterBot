import threading
import time
from collections.abc import Callable, Iterable
from typing import Any, Optional

from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.utils.indexed_event import IndexedEvent


class StreamManager:
    """
    Manages streaming of data through threads and allows hard or soft interruption of the streamed data.
    """

    def __init__(self) -> None:
        """
        Initializes the StreamManager with default values.
        """
        self._events: dict[str, threading.Event] = {
            "indexed": IndexedEvent(),
            "kill": threading.Event(),
            "finalize": threading.Event(),
        }

        self._locks: dict[str, threading.Lock] = {
            "interrupt": threading.Lock(),
            "log": threading.Lock(),
        }

        self._parser: Callable[[IndexedEvent, bool], Any] = lambda x, y: x
        self._parser_finalizer: Optional[Callable[[IndexedEvent], Any]] = None
        self._interrupt: int = 0
        self._idx: int = 0
        self._idx_max: Optional[int] = None
        self._log: list[StreamLogEntry] = []

        self._reset()

    def interrupt(self, timestamp: Optional[int] = None) -> None:
        """
        Interrupts the streaming process.

        Args:
            timestamp (Optional[int]): The timestamp at which to interrupt the stream. Defaults to current time.
        """
        timestamp = time.perf_counter_ns() if not timestamp else timestamp
        with self._locks["interrupt"]:
            self._interrupt = timestamp
        self._events["kill"].set()

    def connect_parser(self, func: Callable[[IndexedEvent, bool], Any]) -> None:
        """
        Connects a parser function for processing each streamed item. The parser function should take an IndexedEvent
        and a boolean indicating whether the stream is on its final iteration.

        Args:
            func (Callable[[IndexedEvent, bool], Any]): The parser function to be used.
        """
        self._parser = func

    def connect_parser_finalizer(self, func: Callable[[IndexedEvent], Any]) -> None:
        """
        Connects a finalizer function for the parser, to be used after streaming is complete.

        Args:
            func (Callable[[IndexedEvent], Any]): The finalizer function to be used.
        """
        self._parser_finalizer = func

    def stream(self, iterable: Iterable[Any], timestamp: Optional[int] = None) -> None:
        """
        Starts streaming data from an iterable source in a separate thread.

        Args:
            iterable (Iterable[Any]): The data source to stream.
            timestamp (Optional[int]): Timestamp marking the start of the stream. Defaults to current time.
        """
        self._reset()

        timestamp = time.perf_counter_ns() if not timestamp else timestamp

        # Creating and starting the parser and stream threads
        parser_thread = threading.Thread(target=self._wrap_parser, kwargs={"timestamp": timestamp}, daemon=True)
        stream_thread = threading.Thread(
            target=self._wrap_stream, kwargs={"iterable": iterable, "timestamp": timestamp}, daemon=True
        )

        parser_thread.start()
        stream_thread.start()

        # Starting the parser finalizer thread if defined
        if self.connect_parser_finalizer is not None:
            parser_finalizer_thread = threading.Thread(target=self._wrap_parser_finalizer, daemon=False)
            parser_finalizer_thread.start()

        self._events["kill"].wait()

        # Joining the parser finalizer thread after completion
        if self.connect_parser_finalizer is not None:
            parser_finalizer_thread.join()

    def _append_to_log(self, value: Any) -> None:
        """
        Appends a value to the stream log.

        Args:
            value (Any): The value to append to the log.
        """
        with self._locks["log"]:
            self._log.append(StreamLogEntry(value=value))

    def _reset(self) -> None:
        """
        Resets the stream manager to its initial state.
        """
        self._idx = 0
        self._log.clear()

        for event in self._events.values():
            event.clear()

    def _wrap_parser(self, timestamp: int) -> None:
        """
        Wraps the parser function to process each item in the stream log.

        Args:
            timestamp (int): The timestamp to start processing from.

        Yields:
            Any: The result of processing a log entry.
        """
        while timestamp < self._interrupt and (self._idx_max is None or self._idx <= self._idx_max):
            self._events["indexed"].wait()
            yield self._parser(self._log[self._idx])
            self._idx += 1
        self._events["finalize"].set()

    def _wrap_parser_finalizer(self) -> None:
        """
        Wraps the parser finalizer function to process remaining items in the stream log.

        Yields:
            Any: The result of processing a log entry using the finalizer.
        """
        self._events["finalize"].wait()
        while self._idx < len(self._log):
            yield self._parser_finalizer(self._log[self._idx])
            self._idx += 1

    def _wrap_stream(self, iterable: Iterable[Any]) -> None:
        """
        Wraps the streaming process for the given iterable.

        Args:
            iterable (Iterable[Any]): The iterable to stream data from.
        """
        for n, value in enumerate(iterable):
            self._append_to_log(value=value)
            self._events["indexed"].increment()
        self._idx_max = n - 1
