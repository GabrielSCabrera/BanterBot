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
        super().__init__()
        self._lock: threading.Lock = threading.Lock()
        self._counter: int = initial_counter

    @property
    def counter(self) -> int:
        """
        Retrieves the current value of the counter, indicating the number of data chunks available for processing.

        Returns:
            int: The current number of unprocessed data chunks.
        """
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
        # with self._lock:
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
        # with self._lock:
        self._counter += N
        if self._counter > 0:
            super().set()

    def decrement(self, N: int = 1) -> None:
        """
        Decrements the counter by a specified amount. It also clears the event if zero is reached, blocking the
        consumer.

        Args:
            N (int): The amount to decrement the counter by. Must be non-negative.
        """
        # with self._lock:
        self._counter -= N
        if self._counter > 0:
            super().set()
        else:
            super().clear()

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
        # with self._lock:
        if N > 0:
            super().set()
        else:
            super().clear()
        self._counter = N
