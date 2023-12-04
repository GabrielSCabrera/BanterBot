import queue
import threading
import time
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
        self._indexed_event = IndexedEvent()

    def close(self) -> None:
        self._closed = True
        self._indexed_event.increment()

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        super().put(item, block, timeout)
        self._indexed_event.increment()

    def finished(self) -> bool:
        return self._closed and self.empty()

    def __iter__(self) -> Self:
        while not self.finished():
            self._indexed_event.wait()
            self._indexed_event.decrement()
            if not self.empty():
                yield super().get()

    def __enter__(self) -> Self:
        return self

    def __exit__(self) -> None:
        self.close()
