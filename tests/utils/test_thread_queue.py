import threading
import time
import unittest

from thread_queue import ThreadQueue


class TestThreadQueue(unittest.TestCase):
    def test_add_task(self):
        thread_queue = ThreadQueue()

        def test_function():
            time.sleep(1)

        thread1 = threading.Thread(target=test_function)
        thread2 = threading.Thread(target=test_function)

        thread_queue.add_task(thread1)
        self.assertEqual(len(thread_queue._event_queue), 1)

        thread_queue.add_task(thread2)
        self.assertEqual(len(thread_queue._event_queue), 2)

    def test_is_alive(self):
        thread_queue = ThreadQueue()

        def test_function():
            time.sleep(1)

        thread1 = threading.Thread(target=test_function)
        thread2 = threading.Thread(target=test_function)

        thread_queue.add_task(thread1)
        self.assertTrue(thread_queue.is_alive())

        thread1.join()
        self.assertFalse(thread_queue.is_alive())

        thread_queue.add_task(thread2)
        self.assertTrue(thread_queue.is_alive())

        thread2.join()
        self.assertFalse(thread_queue.is_alive())

    def test_unskippable(self):
        thread_queue = ThreadQueue()

        def test_function():
            time.sleep(1)

        thread1 = threading.Thread(target=test_function)
        thread2 = threading.Thread(target=test_function)

        thread_queue.add_task(thread1, unskippable=True)
        thread_queue.add_task(thread2)

        start_time = time.time()
        thread1.join()
        thread2.join()
        end_time = time.time()

        self.assertGreaterEqual(end_time - start_time, 2)

    def test_skippable(self):
        thread_queue = ThreadQueue()

        def test_function():
            time.sleep(1)

        thread1 = threading.Thread(target=test_function)
        thread2 = threading.Thread(target=test_function)

        thread_queue.add_task(thread1)
        thread_queue.add_task(thread2)

        start_time = time.time()
        thread1.join()
        thread2.join()
        end_time = time.time()

        self.assertLess(end_time - start_time, 2)


if __name__ == "__main__":
    unittest.main()
