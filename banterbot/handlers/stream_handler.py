import logging
import threading
import time

from banterbot.models.number import Number
from banterbot.utils.closeable_queue import CloseableQueue


class StreamHandler:
    """
    Handler for managing and interacting with a data stream.
    """

    def __init__(
        self,
        interrupt: Number,
        kill_event: threading.Event,
        queue: CloseableQueue,
        processor_thread: threading.Thread,
        shared_data: dict,
    ) -> None:
        """
        Initializes the stream handler with the given parameters. This should not be called directly, but rather
        through the `StreamHandler.create` method. This is because the `StreamHandler` class is not thread-safe.

        Args:
            interrupt (Number): The shared interrupt value.
            kill_event (threading.Event): The shared kill event.
            queue (CloseableQueue): The shared queue.
            processor_thread (threading.Thread): The shared processor thread.
            shared_data (dict): The shared data.
        """
        self._interrupt = interrupt
        self._kill_event = kill_event
        self._queue = queue
        self._shared_data = shared_data
        self._processor_thread = processor_thread

    def __iter__(self) -> CloseableQueue:
        """
        Inherits the `__iter__` method from the `CloseableQueue` class to allow for iteration over the stream handler.
        """
        # Start the processor thread.
        self._processor_thread.start()
        # Prevent multiple iterations over the stream handler.¨
        logging.debug(f"StreamHandler iterating")
        # Return the queue for iteration as a generator.
        for item in self._queue:
            yield item

    def is_alive(self) -> bool:
        """
        Returns whether the stream handler is alive or not.

        Returns:
            bool: Whether the stream handler is alive or not.
        """
        return not self._queue.finished()

    def interrupt(self) -> None:
        """
        Interrupt the active stream by setting the interrupt value to the current time and setting the kill event.
        """
        self._kill_event.set()
        self._interrupt.set(time.perf_counter_ns())
        self._shared_data["interrupt"] = self._interrupt.value
        logging.debug(f"StreamHandler interrupted")
