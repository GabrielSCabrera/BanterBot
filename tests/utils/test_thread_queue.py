import threading
import time
import unittest

from banterbot.utils.thread_queue import ThreadQueue


class TestThreadQueue(unittest.TestCase):
    """
    This test suite includes four test cases:

        1. `test_is_alive`: This test checks if the `is_alive` method correctly reports the status of the last task in
            the queue. It adds a dummy task to the queue and verifies that `is_alive` returns `True` while the task is
            running and `False` after it has completed.

        2. `test_add_task`: This test checks if tasks are added and executed correctly in the queue. It adds a series of
            dummy tasks to the queue and verifies that they are executed in order.

        3. `test_unskippable_task`: This test checks if unskippable tasks are executed correctly in the queue. It adds a
            series of unskippable dummy tasks to the queue and verifies that they are all executed.

        4. `test_skippable_task`: This test checks if skippable tasks are skipped correctly in the queue. It adds a
            series of skippable dummy tasks to the queue and verifies that only the first and last tasks are executed.

        The `setUp` method initializes a `task_counter` list to keep track of the number of times each type of dummy
        task is executed. This is used to verify that the correct number of tasks are executed in each test case.
    """

    def setUp(self):
        self.task_counters = [0, 0, 0]

    def test_is_alive(self):
        thread_queue = ThreadQueue()
        self.assertFalse(thread_queue.is_alive())
        signal = threading.Event()

        def dummy_task(signal):
            signal.wait()

        thread = threading.Thread(target=dummy_task, args=(signal,))
        thread_queue.add_task(thread)

        self.assertTrue(thread_queue.is_alive())
        signal.set()
        t0 = time.perf_counter_ns()
        dt = 0
        timeout = 1e8
        while thread_queue.is_alive() and dt < timeout:
            dt = time.perf_counter_ns() - t0
            time.sleep(0.01)
        self.assertFalse(thread_queue.is_alive())

    def test_add_task(self):
        thread_queue = ThreadQueue()
        signal = threading.Event()

        def dummy_task(signal, N, i):
            self.task_counters[0] += 1
            if i == N - 1:
                signal.set()

        N = 5
        for i in range(N):
            thread = threading.Thread(target=dummy_task, args=(signal, N, i))
            thread_queue.add_task(thread)

        signal.wait()
        self.assertEqual(self.task_counters[0], N)

    def test_unskippable_task(self):
        thread_queue = ThreadQueue()
        signal = threading.Event()

        def dummy_task(signal, N, i):
            self.task_counters[1] += 1
            if i == N - 1:
                signal.set()

        N = 5
        for i in range(N):
            thread = threading.Thread(target=dummy_task, args=(signal, N, i))
            thread_queue.add_task(thread, unskippable=True)

        signal.wait()
        self.assertEqual(self.task_counters[1], N)

    def test_skippable_task(self):
        thread_queue = ThreadQueue()
        signal1 = threading.Event()
        signal2 = threading.Event()

        def dummy_task(signal1, signal2, N, i):
            self.task_counters[2] += 1
            if i == 0:
                signal1.wait()
            elif i == N - 1:
                signal2.set()

        N = 5
        for i in range(N):
            thread = threading.Thread(target=dummy_task, args=(signal1, signal2, N, i))
            thread_queue.add_task(thread)

        signal1.set()
        signal2.wait()
        self.assertEqual(self.task_counters[2], 2)


if __name__ == "__main__":
    unittest.main()
