import threading


class IndexedEvent(threading.Event):
    """
    A thread synchronization event that uses a counter to manage iterations in a producer-consumer scenario. This class
    is ideal for situations where a consumer thread processes data chunks provided by a producer thread. The counter
    ensures that the consumer processes each chunk of data exactly once and waits when no more data is available.

    This class extends threading.Event, adding a counter to control the number of times the event allows passage before
    resetting. It is useful for controlled processing of data chunks in multi-threaded applications, preventing the
    consumer from proceeding until new data is available.
    """

    def __init__(self, initial_counter: int = 0) -> None:
        """
        Initializes the IndexedEvent with an optional initial counter value, which represents the number of items
        initially available for processing.

        Args:
            initial_counter (int): The initial count of items available for processing. Must be non-negative.

        Raises:
            ValueError: If the initial counter is set to a negative value.
        """
        if initial_counter < 0 or not isinstance(initial_counter, int):
            raise ValueError(
                "Argument `initial_counter` in initialization of class `IndexedEvent` must be a non-negative integer."
            )

        super().__init__()
        self._lock: threading.Lock = threading.Lock()

        with self._lock:
            self._counter: int = initial_counter

    @property
    def counter(self) -> int:
        """
        Retrieves the current value of the counter, indicating the number of data chunks available for processing.

        Returns:
            int: The current number of unprocessed data chunks.
        """
        with self._lock:
            return self._counter

    @counter.setter
    def counter(self, N: int) -> None:
        """
        Wrapper for method `set`.

        Args:
            N (int): The number of data chunks available. Must be non-negative.

        Raises:
            ValueError: If N is less than 1 or N is not a number.
        """
        self.set(N=N)

    def clear(self) -> None:
        """
        Resets the event and the counter, typically used to signify that no data is currently available for processing.
        """
        with self._lock:
            super().clear()
            self._counter = 0

    def increment(self, N: int = 1) -> None:
        """
        Increments the counter by a specified amount, indicating that new data chunks are available. It also sets the
        event, allowing the consumer to resume processing.

        Args:
            N (int): The number of new data chunks added. Must be non-negative.

        Raises:
            ValueError: If N is less than 1 or N is not a number.
        """
        if N < 0 or not isinstance(N, int):
            raise ValueError(
                "Argument `N` in class `IndexedEvent` method `increment(N: int)` must be a non-negative integer."
            )

        with self._lock:
            self._counter += N
            super().set()

    def is_set(self) -> bool:
        """
        Checks if the event is set, meaning data is available for processing.

        Returns:
            bool: True if data is available, False otherwise.
        """
        return super().is_set()

    def set(self, N: int = 1) -> None:
        """
        Directly sets the counter to a specified value, indicating the exact number of data chunks available.

        Args:
            N (int): The number of data chunks available. Must be non-negative.

        Raises:
            ValueError: If N is less than 1 or N is not a number.
        """
        if N < 0 or not isinstance(N, int):
            raise ValueError(
                "Argument `N` in class `IndexedEvent` method `set(N: int)` must be a non-negative integer."
            )
        with self._lock:
            self._counter = N
            if self._counter > 0:
                super().set()
            else:
                super().clear()

    def wait(self, timeout: float = None) -> bool:
        """
        Waits for the event to be set (data to be available), then decrements the counter, indicating a data chunk has
        been processed. If the counter reaches zero, indicating no more data, the event is cleared.

        Args:
            timeout (float): Optional timeout for the wait.

        Returns:
            bool: True if the event was set (data was processed), False if it timed out.
        """
        with self._lock:
            self._counter = self._counter - 1 if self._counter > 0 else self._counter
        if self._counter <= 0:
            return super().wait(timeout)
        return True
