import threading
from collections import UserDict
from typing import Any, Iterator


class SharedData(UserDict):
    """
    A thread-safe shared data structure based on a dictionary. This class provides a safe way to share data between
    threads by ensuring atomic operations for setting, getting, deleting, and iterating over items. It also supports
    appending to lists within the dictionary. If a key does not exist, a `None` value is returned instead of raising
    a KeyError.

    Inherits from UserDict to provide a dictionary-like interface.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the SharedData object with an optional initial dictionary and additional keyword arguments.

        Args:
            *args (variable): Optional dictionary to initialize the SharedData object.
            **kwargs (dict): Additional keyword arguments to pass to the UserDict initializer.
        """
        super().__init__(*args, **kwargs)
        self._lock = threading.RLock()

    def __getitem__(self, key: str) -> Any:
        """
        Retrieves the value associated with the given key. Returns `None` if the key does not exist.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            Any: The value associated with the key, or `None` if the key does not exist.
        """
        with self._lock:
            return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets the given key to the specified value.

        Args:
            key (str): The key to be set.
            value (Any): The value to set for the key.
        """
        with self._lock:
            self.data[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Deletes the specified key from the dictionary, if it exists.

        Args:
            key (str): The key to be deleted.
        """
        with self._lock:
            if key in self.data:
                del self.data[key]

    def __contains__(self, key: str) -> bool:
        """
        Checks if the dictionary contains the specified key.

        Args:
            key (str): The key to check for in the dictionary.

        Returns:
            bool: True if the key exists in the dictionary, False otherwise.
        """
        with self._lock:
            return key in self.data

    def __iter__(self) -> Iterator[str]:
        """
        Provides an iterator over the keys of the dictionary.

        Yield:
            Iterator[str]: An iterator over the keys of the dictionary.
        """
        with self._lock:
            return iter(self.data.keys())

    def __len__(self) -> int:
        """
        Returns the number of items in the dictionary.

        Returns:
            int: The number of items in the dictionary.
        """
        with self._lock:
            return len(self.data)

    def clear(self) -> None:
        """
        Clears all keys and values from the dictionary.
        """
        with self._lock:
            self.data.clear()

    def append(self, key: str, value: Any) -> None:
        """
        Appends a value to a list associated with the given key. If the key does not exist, a new list is created.

        Args:
            key (str): The key associated with the list to append to.
            value (Any): The value to append to the list.
        """
        with self._lock:
            if key not in self.data:
                self.data[key] = []
            self.data[key].append(value)
