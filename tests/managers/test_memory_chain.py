import datetime
import unittest

from banterbot import config
from banterbot.data.enums import ChatCompletionRoles
from banterbot.managers.memory_chain import MemoryChain
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message


class TestMemoryChain(unittest.TestCase):
    """
    This test suite includes tests for the `MemoryChain` class. It tests the following functionalities:

        1. `setUp`: This method is called before each test case. It creates a new `MemoryChain` instance, appends a
            single memory, and extends the instance with a list of memories.

        2. `test_search_exact`: This test case checks if the `search` method returns the correct number of memories when
            searching for an exact keyword match.

        3. `test_search_fuzzy`: This test case checks if the `search` method returns the correct number of memories when
            searching with a fuzzy threshold.

        4. `test_search_fuzzy_threshold`: This test case checks if the `search` method returns the correct number of
            memories when searching with a different fuzzy threshold.

        5. `test_load_and_search`: This test case checks if the `load` method correctly loads a `MemoryChain` instance
            and if the loaded instance can perform search operations correctly.

        6. `tearDown`: This method is called after each test case. It deletes the `MemoryChain` instance and checks if
            the associated directory is removed.
    """

    def setUp(self):
        self.memory_chain = MemoryChain.create()
        self.uuid = self.memory_chain.uuid
        msg1 = Message(ChatCompletionRoles.ASSISTANT, "Hello")
        msg2 = Message(ChatCompletionRoles.ASSISTANT, "Hi")
        msg3 = Message(ChatCompletionRoles.ASSISTANT, "How are you?")
        memory = Memory(["dog", "cat"], "memory1 summary", 60, datetime.datetime.now(), [msg1, msg2])
        self.memory_chain.append(memory)
        memories = [
            Memory(["car", "feline"], "memory2 summary", 80, datetime.datetime.now(), [msg2]),
            Memory(["eat", "drive"], "memory3 summary", 70, datetime.datetime.now(), [msg1, msg3]),
        ]
        self.memory_chain.extend(memories)

    def test_search_exact(self):
        memories = self.memory_chain.search(["cat"])
        self.assertEqual(len(memories), 1)

    def test_search_fuzzy(self):
        memories = self.memory_chain.search(["cat"], fuzzy_threshold=0.5)
        self.assertEqual(len(memories), 2)

    def test_search_fuzzy_threshold(self):
        memories = self.memory_chain.search(["drive"], fuzzy_threshold=0.3)
        self.assertEqual(len(memories), 2)

    def test_load_and_search(self):
        loaded_memory_chain = MemoryChain.load(uuid=self.uuid)

        memories = loaded_memory_chain.search(["cat"])
        self.assertEqual(len(memories), 1)

        memories_fuzzy = loaded_memory_chain.search(["cat"], fuzzy_threshold=0.5)
        self.assertEqual(len(memories_fuzzy), 2)

        memories_fuzzy_threshold = loaded_memory_chain.search(["drive"], fuzzy_threshold=0.3)
        self.assertEqual(len(memories_fuzzy_threshold), 2)

        self.assertEqual(loaded_memory_chain.uuid, self.memory_chain.uuid)

    def tearDown(self):
        MemoryChain.delete(uuid=self.uuid)
        path = config.personae / self.uuid
        self.assertTrue(not path.exists())


if __name__ == "__main__":
    unittest.main()
