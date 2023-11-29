import threading
import time

from banterbot.utils.closable_queue import ClosableQueue
from banterbot.utils.number import Number


class StreamHandler:
    """
    Handler for managing and interacting with a data stream.
    """

    def __init__(
        self, interrupt: Number, kill_event: threading.Event, queue: ClosableQueue, processor_thread: threading.Thread
    ) -> None:
        """
        Initializes the stream handler with the given parameters. This should not be called directly, but rather
        through the `StreamHandler.create` method. This is because the `StreamHandler` class is not thread-safe.

        Args:
            interrupt (Number): The shared interrupt value.
            kill_event (threading.Event): The shared kill event.
            queue (ClosableQueue): The shared queue.
            processor_thread (threading.Thread): The shared processor thread.
        """
        self._interrupt = interrupt
        self._kill_event = kill_event
        self._queue = queue
        self._iterating = False

        processor_thread.start()
        processor_thread.join()

    def __iter__(self) -> ClosableQueue:
        """
        Inherits the `__iter__` method from the `ClosableQueue` class to allow for iteration over the stream handler.
        """
        # Prevent multiple iterations over the stream handler.
        with self._close_lock:
            if self._iterating:
                raise RuntimeError("Cannot iterate over the same instance of `StreamHandler` more than once.")
            self._iterating = True

            # Return the queue for iteration as a generator.
            return iter(self._queue)

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
        self._interrupt.value = time.perf_counter_ns()
