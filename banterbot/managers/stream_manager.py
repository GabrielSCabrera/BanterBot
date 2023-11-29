import inspect
import threading
import time
from collections.abc import Callable, Iterable
from copy import deepcopy
from typing import Any, Optional

from banterbot.handlers.stream_handler import StreamHandler
from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.utils.closable_queue import ClosableQueue
from banterbot.utils.indexed_event import IndexedEvent
from banterbot.utils.number import Number


class StreamManager:
    """
    Manages streaming of data through threads and allows hard or soft interruption of the streamed data.
    """

    def __init__(self) -> None:
        """
        Initializes the StreamManager with default values.
        """
        self._processor: Callable[[IndexedEvent, int, dict], Any] = None
        self._exception_handler: Optional[Callable[[IndexedEvent, dict], Any]] = None
        self._completion_handler: Callable[[IndexedEvent, int, dict], Any] = None

    def connect_processor(self, func: Callable[[list[StreamLogEntry], int, dict], Any]) -> None:
        """
        Connects a processor function for processing each streamed item. The stream processor function should take a
        list of `StreamLogEntry` instances, the current index of the log, and a dictionary which will contain shared
        data between the connected functions.

        Args:
            func (Callable[[list[StreamLogEntry], int, dict], Any]): The stream processor function to be used.
        """
        if inspect.signature(func).parameters != ["log", "index", "shared_data"]:
            raise ValueError(
                "Argument `func` in method `connect_processor` of class `StreamManager` expects the following"
                " signature: `func(log: list[StreamLogEntry], index: int, shared_data: dict) -> Any`."
            )
        self._processor = func

    def connect_completion_handler(self, func: Callable[[list[StreamLogEntry], dict], Any]) -> None:
        """
        Connects an optional completion handler function for handling the final result of the parser. The handler
        function should take a list of `StreamLogEntry` instances and a dictionary which will contain shared data
        between the connected functions.

        Args:
            func (Callable[[list[StreamLogEntry], dict], Any]): The completion handler function to be used.
        """
        if inspect.signature(func).parameters != ["log", "shared_data"]:
            raise ValueError(
                "Argument `func` in method `connect_completion_handler` of class `StreamManager`  expects the following"
                " signature: `func(log: list[StreamLogEntry], shared_data: dict) -> Any`."
            )

        self._completion_handler = func

    def connect_exception_handler(self, func: Callable[[list[StreamLogEntry], int, dict], Any]) -> None:
        """
        Connects an optional exception handler function for the parser, to be used when the stream iterable is
        interrupted. The stream exception handler function is provided with the log and the current index for all
        remaining items in thestream. The handler function should take a list of `StreamLogEntry` instances, the
        current index of the log, and a dictionary which will contain shared data between the connected functions.

        Args:
            func (Callable[[list[StreamLogEntry], int, dict], Any]): The finalizer function to be used.
        """
        if inspect.signature(func).parameters != ["log", "index", "shared_data"]:
            raise ValueError(
                "Argument `func` in method `connect_exception_handler` of class `StreamManager`  expects the following"
                " signature: `func(log: list[StreamLogEntry], index: int, shared_data: dict) -> Any`."
            )
        self._exception_handler = func

    def stream(
        self,
        iterable: Iterable[Any],
        close_stream: Optional[Callable] = None,
        init_shared_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Starts streaming data from an iterable source in a separate thread.

        Args:
            iterable (Iterable[Any]): The iterable to stream data from.
            close_stream (Optional[str]): The method to use for closing the iterable.
            init_shared_data (Optional[dict[str, Any]]): The initial shared data to use.
        """
        # Getting the timestamp of the stream.
        timestamp = time.perf_counter_ns()

        # Checking if a stream processor function has been connected, and raising an error if not.
        if self._processor is None:
            raise ValueError(
                "No processor function has been connected. Please use the `connect_processor` method to connect a"
                " processor function."
            )

        # Creating the indexed event and kill event to be used.
        indexed_event = IndexedEvent()
        kill_event = threading.Event()

        # Creating the interrupt, index, and index_max values to be used.
        interrupt = Number(value=0)
        index_max = Number(None)

        # Creating the queue and log to be used.
        queue = ClosableQueue()
        log = []

        # Creating copies of the stream processor, completion handler, and exception handler to be used.
        processor = deepcopy(self._processor)
        completion_handler = self._completion_handler if deepcopy(self._completion_handler) else None
        exception_handler = self._exception_handler if deepcopy(self._exception_handler) else None

        # Creating the stream thread with the `_wrap_stream` method as the target function.
        stream_thread = threading.Thread(
            target=self._wrap_stream,
            kwargs={
                "index_max": index_max,
                "indexed_event": indexed_event,
                "kill_event": kill_event,
                "log": log,
                "iterable": iterable,
                "close_stream": close_stream,
            },
            daemon=False,
        )

        # Creating the stream processor thread with the `_wrap_stream_processor` method as the target function.
        processor_thread = threading.Thread(
            target=self._wrap_processor,
            kwargs={
                "timestamp": timestamp,
                "interrupt": interrupt,
                "index_max": index_max,
                "indexed_event": indexed_event,
                "queue": queue,
                "log": log,
                "processor": processor,
                "completion_handler": completion_handler,
                "exception_handler": exception_handler,
                "init_shared_data": init_shared_data,
            },
            daemon=True,
        )

        # Starting the stream processor and stream threads.
        stream_thread.start()

        # Return an instance of StreamHandler
        return StreamHandler(
            interrupt=interrupt,
            kill_event=kill_event,
            queue=queue,
            processor_thread=processor_thread,
        )

    def _wrap_stream(
        self,
        index_max: Number,
        indexed_event: IndexedEvent,
        kill_event: threading.Event,
        log: list[StreamLogEntry],
        iterable: Iterable[Any],
        close_stream: Optional[str] = None,
    ) -> None:
        """
        Wraps the `_stream` thread to allow for instant interruption using the `kill` event.

        Args:
            index_max (Number): The maximum index to stream to.
            indexed_event (IndexedEvent): The indexed event to use for tracking the current index.
            kill_event (threading.Event): The event to use for interrupting the stream.
            log (list[StreamLogEntry]): The log to store streamed data in.
            iterable (Iterable[Any]): The iterable to stream data from.
            close_stream (Optional[str]): The method to use for closing the iterable.
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

        # Closing the iterable if the stream thread is still alive and a callable that closes the stream is defined.
        if thread.is_alive() and close_stream:
            # Close the iterable using the provided method-closing callable.
            close_stream()

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

    def _wrap_processor(
        self,
        timestamp: float,
        interrupt: Number,
        index_max: Number,
        indexed_event: IndexedEvent,
        queue: ClosableQueue,
        log: list[StreamLogEntry],
        processor: Callable[[list[StreamLogEntry], int, dict], Any],
        completion_handler: Optional[Callable[[list[StreamLogEntry], dict], Any]],
        exception_handler: Callable[[list[StreamLogEntry], int, dict], Any],
        init_shared_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Wraps the parser function to process each item in the stream log.

        Args:
            timestamp (float): The timestamp of the stream.
            interrupt (Number): The interrupt time of the stream.
            index_max (Number): The maximum index to stream to.
            indexed_event (IndexedEvent): The indexed event to use for tracking the current index.
            queue (ClosableQueue): The queue to store processed data in.
            log (list[StreamLogEntry]): The log to store streamed data in.
            stream_processor (Callable[[list[StreamLogEntry], int, dict], Any]): The stream processor function to
                be used.
            stream_completion_handler (Optional[Callable[[list[StreamLogEntry], dict], Any]]): The completion
                handler function to be used.
            stream_exception_handler (Callable[[list[StreamLogEntry], int, dict], Any]): The exception handler
                function to be used.
        """
        index = 0
        if init_shared_data:
            shared_data = deepcopy(init_shared_data)
        else:
            shared_data = dict()

        while timestamp < interrupt and (index_max.value is None or index <= index_max):
            indexed_event.wait()
            queue.put(processor(log=log, index=index, shared_data=shared_data))
            index += 1
        else:
            if timestamp < interrupt and completion_handler:
                queue.put(completion_handler(log=log, shared_data=shared_data))

        if exception_handler:
            while index < len(log):
                queue.put(exception_handler(log=log, index=index, shared_data=shared_data))
                index += 1
        queue.close()
