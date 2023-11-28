import queue
import threading
from typing import Any, Optional

from typing_extensions import Self


class ClosableQueue(queue.Queue):
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

    def __init__(self) -> None:
        super().__init__()
        self._closed = False
        self._in_context = False
        self._close_lock = threading.Lock()

    def close(self) -> None:
        with self._close_lock:
            self._closed = True
            self.all_tasks_done.notify_all()

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        if not self._in_context:
            raise RuntimeError(
                "Method `put(item: Any, block: bool, timeout: Optional[float])` in class `ClosableQueue` was called"
                " outside of a context manager."
            )
        with self._close_lock:
            if self._closed:
                raise RuntimeError(
                    "Method `put(item: Any, block: bool, timeout: Optional[float])` in class `ClosableQueue` was called"
                    " after the instance was closed."
                )
            else:
                super().put(item, block, timeout)

    def closed(self) -> bool:
        with self._close_lock:
            return self._closed

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Any:
        with self._close_lock:
            if not self.empty() or not self._closed:
                return self.get()
            raise StopIteration

    def __enter__(self) -> Self:
        if self._in_context:
            raise RuntimeError(
                "Method `__enter__()` in class `ClosableQueue` was called while the instance was already in a context"
            )
        self._in_context = True
        return self

    def __exit__(self) -> None:
        self._in_context = False
        self.close()
