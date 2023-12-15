import threading
import time
import unittest

from banterbot.utils.barrier import Barrier


class TestIndexedEvent(unittest.TestCase):
    def test_initial_counter(self):
        event = Barrier(initial_counter=5)
        self.assertEqual(event.counter, 5)

    def test_set_counter(self):
        event = Barrier()
        event.counter = 3
        self.assertEqual(event.counter, 3)

    def test_set_negative_counter(self):
        event = Barrier()
        with self.assertRaises(ValueError):
            event.counter = -1

    def test_clear_event(self):
        event = Barrier(initial_counter=5)
        event.clear()
        self.assertEqual(event.counter, 0)
        self.assertFalse(event.is_set())

    def test_increment_counter(self):
        event = Barrier()
        event.increment(2)
        self.assertEqual(event.counter, 2)
        self.assertTrue(event.is_set())

    def test_increment_negative_counter(self):
        event = Barrier()
        with self.assertRaises(ValueError):
            event.increment(-1)

    def test_set_event(self):
        event = Barrier()
        event.set(3)
        self.assertEqual(event.counter, 3)
        self.assertTrue(event.is_set())

    def test_set_negative_event(self):
        event = Barrier()
        with self.assertRaises(ValueError):
            event.set(-1)

    def test_wait_event(self):
        event = Barrier(initial_counter=3)

        def consumer():
            time.sleep(1)
            event.wait()
            self.assertEqual(event.counter, 2)

        thread = threading.Thread(target=consumer)
        thread.start()

        event.increment()
        event.increment()
        event.increment()

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())

    def test_wait_timeout(self):
        event = Barrier(initial_counter=1)
        self.assertFalse(event.wait(timeout=0.5))

    def test_wait_zero_counter(self):
        event = Barrier(initial_counter=0)
        self.assertFalse(event.wait(timeout=0.5))


if __name__ == "__main__":
    unittest.main()
