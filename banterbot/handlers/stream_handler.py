import threading
from typing import Any, Callable, Optional

from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.utils.number import Number
from banterbot.utils.shared_data import SharedData


class StreamHandler:
    """
    Handler for managing and interacting with a data stream.
    """

    def __init__(
        self,
        stream_thread: threading.Thread,
        kill_event: threading.Event,
        log: list[StreamLogEntry],
        stream_processor: Callable[[list[StreamLogEntry], int, SharedData], Any],
        stream_finalizer: Optional[Callable[[list[StreamLogEntry], SharedData], Any]],
    ):
        self._stream_thread = stream_thread
        self._kill_event = kill_event
        self._log = log
        self._stream_processor = stream_processor
        self._stream_finalizer = stream_finalizer

        self._shared_data = SharedData()
        self._finalize_event = threading.Event()
        self._interrupt = Number(value=0)
        self._index = Number(value=0)

    def interrupt(self):
        """
        Interrupt the active stream.
        """
        self._kill_event.set()
        if self._stream_finalizer:
            self._stream_finalizer(log=self._log, shared_data=self._shared_data)

    def __iter__(self):
        """
        Allow iteration over the streamed values.
        """
        return self

    def __next__(self):
        """
        Return the next item from the stream after processing it.
        """
        if self._index < len(self._log):
            entry = self._log[self._index]
            processed_entry = self._stream_processor(entry, self._index, self._shared_data)
            self._index += 1
            return processed_entry
        else:
            raise StopIteration
