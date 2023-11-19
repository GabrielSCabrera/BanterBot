import logging
import threading


class ThreadQueue:
    """
    A class for managing and executing tasks in separate threads.

    This class maintains a queue of tasks to be executed. Each task is a Thread object, which is executed in its own
    thread. If there is a task in the queue that hasn't started executing yet, it will be prevented from running when a
    new task is added unless it is declared unskippable.
    """

    def __init__(self):
        logging.debug(f"ThreadQueue initialized")
        self._lock = threading.Lock()
        self._event_queue: list[threading.Event] = []

    def is_alive(self) -> bool:
        """
        Check if the last task in the queue is still running.

        Returns:
            bool: True if the last task is still running, False otherwise.
        """
        if not self._event_queue:
            return False
        else:
            return not self._event_queue[-1].is_set()

    def add_task(self, thread: threading.Thread, unskippable: bool = False) -> None:
        """
        Add a new task to the queue.

        This method adds a new task to the queue and starts a wrapper thread to manage its execution. The wrapper thread
        is responsible for waiting for the previous task to complete, executing the current task if it is unskippable or
        the last task in the queue, and setting the event for the next task.

        Args:
            thread (threading.Thread): The thread to be added to the queue.
            unskippable (bool, optional): Whether the thread should be executed even if a new task is queued.
        """
        with self._lock:
            index = len(self._event_queue)
            self._event_queue.append(threading.Event())

        wrapper_thread = threading.Thread(
            target=self._thread_wrapper, args=(thread, index, unskippable), daemon=thread.daemon
        )
        wrapper_thread.start()

    def _thread_wrapper(self, thread: threading.Thread, index: int, unskippable: bool) -> None:
        """
        A wrapper function for executing threads in the queue.

        This function is responsible for waiting for the previous task to complete before starting the current task, and
        setting the event for the next task in the queue. If the current task is skippable and not the last task in the
        queue, it will not be executed.

        Args:
            thread (threading.Thread): The thread to be executed.
            index (int): The index of the thread in the event queue.
            unskippable (bool): Whether the thread should be executed even if a new task is added to the queue.
        """
        if index > 0:
            self._event_queue[index - 1].wait()

        if unskippable or index == len(self._event_queue) - 1:
            logging.debug(f"ThreadQueue thread {index} started")
            thread.start()
            thread.join()
        else:
            logging.debug(f"ThreadQueue thread {index} skipped")

        self._event_queue[index].set()
