import inspect
import threading
import time
from collections.abc import Callable, Generator, Iterable
from typing import Any, Optional

from banterbot.handlers.stream_handler import StreamHandler
from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.utils.indexed_event import IndexedEvent
from banterbot.utils.number import Number
from banterbot.utils.shared_data import SharedData


class StreamManager:
    """
    Manages streaming of data through threads and allows hard or soft interruption of the streamed data.
    """

    def __init__(self) -> None:
        """
        Initializes the StreamManager with default values.
        """
        self._stream_processor: Callable[[IndexedEvent, int, SharedData], Any] = lambda x, y: x
        self._stream_finalizer: Optional[Callable[[IndexedEvent, SharedData], Any]] = None

    def connect_stream_processor(self, func: Callable[[list[StreamLogEntry], int, SharedData], Any]) -> None:
        """
        Connects a parser function for processing each streamed item. The parser function should take an IndexedEvent,
        the current index, and a dictionary, which will contain shared data between the connected functions.

        Args:
            func (Callable[[list[StreamLogEntry], int, SharedData], Any]): The parser function to be used.
        """
        if inspect.signature(func).parameters != ["log", "index", "shared_data"]:
            raise ValueError(
                "Argument `func` in method `connect_stream_processor` of class `StreamManager` should have the"
                " following signature: `func(log: list[StreamLogEntry], index: int, shared: SharedData) -> Any`."
            )
        self._stream_processor = func

    def connect_stream_completion_handler(self, func: Callable[[list[StreamLogEntry], SharedData], Any]) -> None:
        """
        Connects a stream completion handler function for handling the final result of the parser. The handler function
        should take an IndexedEvent and a dictionary, which will contain shared data between the connected functions.

        Args:
            func (Callable[[list[StreamLogEntry], SharedData], Any]): The completion handler function to be used.
        """
        if inspect.signature(func).parameters != ["log", "shared_data"]:
            raise ValueError(
                "Argument `func` in method `connect_stream_processor` of class `StreamManager` should have the"
                " following signature: `func(log: list[StreamLogEntry], shared: SharedData) -> Any`."
            )

        self._stream_completion_handler = func

    def connect_stream_finalizer(self, func: Callable[[list[StreamLogEntry], int, SharedData], Any]) -> None:
        """
        Connects a finalizer function for the parser, to be used after streaming is complete. The finalizer function
        should take an IndexedEvent, the current index, and a dictionary, which will contain shared data between the
        connected functions.

        Args:
            func (Callable[[list[StreamLogEntry], int, SharedData], Any]): The finalizer function to be used.
        """
        if inspect.signature(func).parameters != ["log", "index", "shared_data"]:
            raise ValueError(
                "Argument `func` in method `connect_stream_processor` of class `StreamManager` should have the"
                " following signature: `func(log: list[StreamLogEntry], index: int, shared_data: SharedData) -> Any`."
            )
        self._stream_finalizer = func

    def stream(
        self, iterable: Iterable[Any], close_method: Optional[str] = None, timestamp: Optional[int] = None
    ) -> None:
        """
        Starts streaming data from an iterable source in a separate thread.

        Args:
            iterable (Iterable[Any]): The iterable to stream data from.
            close_method (Optional[str]): The method to use for closing the iterable.
            timestamp (Optional[int]): The timestamp to start processing from.
        """

        indexed_event = IndexedEvent()
        kill_event = threading.Event()

        index_max = Number(None)
        log = []

        timestamp = time.perf_counter_ns() if not timestamp else timestamp

        # # Creating the stream processor thread with the `_wrap_stream_processor` method as the target function.
        # processor_thread = threading.Thread(
        #     target=self._wrap_stream_processor,
        #     kwargs={
        #         "timestamp": timestamp,
        #         "interrupt": interrupt,
        #         "finalize_event": finalize_event,
        #         "indexed_event": indexed_event,
        #         "log": log,
        #         "index": index,
        #         "index_max": index_max,
        #         "shared_data": shared_data,
        #     },
        #     daemon=True,
        # )

        # Creating the stream thread with the `_wrap_stream` method as the target function.
        stream_thread = threading.Thread(
            target=self._wrap_stream,
            kwargs={
                "index_max": index_max,
                "indexed_event": indexed_event,
                "kill_event": kill_event,
                "log": log,
                "iterable": iterable,
                "close_method": close_method,
            },
            daemon=True,
        )

        # Starting the stream processor and stream threads.
        # processor_thread.start()
        stream_thread.start()

        # Return an instance of StreamHandler
        return StreamHandler(stream_thread, kill_event, log)

        # # Starting the parser finalizer thread if defined
        # if self.connect_stream_finalizer is not None:
        #     parser_finalizer_thread = threading.Thread(
        #         target=self._wrap_stream_finalizer,
        #         kwargs={
        #             "finalize_event": finalize_event,
        #             "log": log,
        #             "index": index,
        #             "shared_data": shared_data,
        #         },
        #         daemon=False,
        #     )
        #     parser_finalizer_thread.start()

        # # Joining the parser finalizer thread after completion
        # if self.connect_stream_finalizer is not None:
        #     parser_finalizer_thread.join()

    def _wrap_stream(
        self,
        index_max: Number,
        indexed_event: IndexedEvent,
        kill_event: threading.Event,
        log: list[StreamLogEntry],
        iterable: Iterable[Any],
        close_method: Optional[str] = None,
    ) -> None:
        """
        Wraps the `_stream` thread to allow for instant interruption using the `kill` event.

        Args:
            index_max (Number): The maximum index to stream to.
            indexed_event (IndexedEvent): The indexed event to use for tracking the current index.
            kill_event (threading.Event): The event to use for interrupting the stream.
            log (list[StreamLogEntry]): The log to store streamed data in.
            iterable (Iterable[Any]): The iterable to stream data from.
            close_method (Optional[str]): The method to use for closing the iterable.
        """
        # Instantiating the stream thread with the `_stream` method as the target function.
        thread = threading.Thread(
            self._stream,
            kwargs={
                "index_max": index_max,
                "indexed_event": indexed_event,
                "kill_event": kill_event,
                "log": log,
                "iterable": iterable,
            },
            daemon=True,
        )
        # Starting the stream thread.
        thread.start()

        # Waiting for the kill event to be set.
        kill_event.wait()

        # Closing the iterable if the stream thread is still alive and a close method is defined.
        if thread.is_alive() and close_method:
            # Close the iterable if it has a close method.
            getattr(iterable, close_method)()

    def _stream(
        self,
        index_max: Number,
        indexed_event: IndexedEvent,
        kill_event: threading.Event,
        log: list[StreamLogEntry],
        iterable: Iterable[Any],
    ) -> None:
        """
        Wraps the streaming process for the given iterable.

        Args:
            index_max (Number): The maximum index to stream to.
            indexed_event (IndexedEvent): The indexed event to use for tracking the current index.
            kill_event (threading.Event): The event to use for interrupting the stream.
            log (list[StreamLogEntry]): The log to store streamed data in.
            iterable (Iterable[Any]): The iterable to stream data from.
        """
        for n, value in enumerate(iterable):
            log.append(StreamLogEntry(value=value))
            indexed_event.increment()
        index_max.set(n - 1)
        kill_event.set()

    def _wrap_stream_finalizer(
        self,
        finalize_event: threading.Event,
        log: list[StreamLogEntry],
        index: Number,
        shared_data: SharedData,
    ) -> Generator[Any, None, None]:
        """
        Wraps the parser finalizer function to process remaining items in the stream log.

        Args:
            finalize_event (threading.Event): The event to use for finalizing the stream.
            log (list[StreamLogEntry]): The log to store streamed data in.
            index (Number): The index to start processing from.
            shared_data (SharedData): The shared dictionary to use for processing.

        Yields:
            Any: The result of processing a log entry.
        """
        finalize_event.wait()
        while index < len(log):
            yield self._stream_finalizer(log=log, index=index, shared_data=shared_data)
            index += 1

    def _wrap_stream_processor(
        self,
        timestamp: int,
        interrupt: Number,
        finalize_event: threading.Event,
        indexed_event: IndexedEvent,
        log: list[StreamLogEntry],
        index: Number,
        index_max: Number,
        shared_data: SharedData,
    ) -> None:
        """
        Wraps the parser function to process each item in the stream log.

        Args:
            timestamp (int): The timestamp to start processing from.
            shared_data (dict): The shared dictionary to use for processing.

        Yields:
            Any: The result of processing a log entry.
        """
        while timestamp < interrupt and (index_max.value is None or index <= index_max):
            indexed_event.wait()
            yield self._stream_processor(log=log, index=index, shared_data=shared_data)
            index += 1
        else:
            yield self._stream_completion_handler(log=log, shared_data=shared_data)
        finalize_event.set()
