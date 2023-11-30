import threading
import time
import unittest

from banterbot.utils.closeable_queue import CloseableQueue


class TestCloseableQueue(unittest.TestCase):
    def test_put_and_get(self):
        queue = CloseableQueue()
        queue.put(1)
        queue.put(2)
        self.assertEqual(queue.get(), 1)
        self.assertEqual(queue.get(), 2)

    def test_put_after_close(self):
        queue = CloseableQueue()
        queue.close()
        with self.assertRaises(RuntimeError):
            queue.put(1)

    def test_get_after_close(self):
        queue = CloseableQueue()
        queue.put(1)
        queue.close()
        self.assertEqual(queue.get(), 1)
        with self.assertRaises(StopIteration):
            queue.get()

    def test_finished(self):
        queue = CloseableQueue()
        self.assertFalse(queue.finished())
        queue.put(1)
        self.assertFalse(queue.finished())
        queue.close()
        self.assertFalse(queue.finished())
        queue.get()
        self.assertTrue(queue.finished())

    def test_iteration(self):
        queue = CloseableQueue()
        queue.put(1)
        queue.put(2)
        queue.put(3)
        queue.close()

        items = []
        for item in queue:
            items.append(item)

        self.assertEqual(items, [1, 2, 3])

    def test_context_manager(self):
        def producer(queue):
            with queue:
                queue.put(1)
                queue.put(2)
                queue.put(3)

        queue = CloseableQueue()
        thread = threading.Thread(target=producer, args=(queue,))
        thread.start()

        items = []
        for item in queue:
            items.append(item)

        thread.join()
        self.assertEqual(items, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
