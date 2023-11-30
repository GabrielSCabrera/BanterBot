import queue
import threading
from typing import Any, Optional

from typing_extensions import Self

from banterbot.utils.indexed_event import IndexedEvent


class CloseableQueue(queue.Queue):
    """
    A queue that can be closed to prevent further puts. This is useful for when you have a producer thread that you
    want to stop once it has finished producing items, but you don't want to stop the consumer thread from consuming
    items that have already been produced. Must be used as a context manager on the producer thread to ensure that the
    queue is closed when the producer thread exits.

    The intended use case is that the producer thread will put items into the queue until it is finished, then close the
    queue and exit. The consumer thread will then consume the items in the queue until it is empty, ideally using a
    `for` loop to ensure that it exits when the queue is empty and closed.

    If a `for` loop is not used by the consumer thread, then the consumer thread can also use a `while` loop to consume
    items from the queue. In this case, the `while` loop's condition should be `while not queue.closed()` to ensure that
    the consumer thread exits when the queue is empty and closed.
    """

    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize=maxsize)
        self._closed = False
        self._in_context = False
        self._iterating_lock = threading.Lock()
        self._context_lock = threading.Lock()
        self._indexed_event = IndexedEvent()
        self._iterating = False

    def close(self) -> None:
        self._closed = True
        self._indexed_event.increment()

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        if self._closed:
            raise RuntimeError(
                "Method `put(item: Any, block: bool, timeout: Optional[float])` in class `CloseableQueue` was"
                " called after the instance was closed."
            )
        else:
            super().put(item, block, timeout)
            self._indexed_event.increment()

    def finished(self) -> bool:
        return self._closed and self.empty()

    def __iter__(self) -> Self:
        with self._iterating_lock:
            if self._iterating:
                raise RuntimeError(
                    "Method `__iter__()` in class `CloseableQueue` was called while the instance was already iterating."
                )
            self._iterating = True

        while not self.finished():
            self._indexed_event.wait()
            if not self.empty():
                yield super().get()

    def __enter__(self) -> Self:
        with self._context_lock:
            if self._in_context:
                raise RuntimeError(
                    "Method `__enter__()` in class `CloseableQueue` was called while the instance was already in a"
                    " context."
                )
            self._in_context = True
            return self

    def __exit__(self) -> None:
        self._in_context = False
        self.close()
