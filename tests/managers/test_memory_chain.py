import datetime
import unittest

from banterbot.data.enums import ChatCompletionRoles
from banterbot.managers.memory_chain import MemoryChain
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message


class TestMemoryChain(unittest.TestCase):
    def setUp(self):
        # Creating new memory manager
        self.memory_manager = MemoryChain.create()
        self.uuid = self.memory_manager.uuid

        # Create a few sample messages
        self.msg1 = Message(ChatCompletionRoles.ASSISTANT, "Hello")
        self.msg2 = Message(ChatCompletionRoles.ASSISTANT, "Hi")
        self.msg3 = Message(ChatCompletionRoles.ASSISTANT, "How are you?")

        # Append new memory
        memory = Memory(["dog", "cat"], "memory1 summary", 0.6, datetime.datetime.now(), [self.msg1, self.msg2])
        self.memory_manager.append(memory)

        # Extend with new memories
        memories = [
            Memory(["car", "feline"], "memory2 summary", 0.8, datetime.datetime.now(), [self.msg2]),
            Memory(["eat", "drive"], "memory3 summary", 0.7, datetime.datetime.now(), [self.msg1, self.msg3]),
        ]
        self.memory_manager.extend(memories)

    def test_search_exact_keyword(self):
        memories = self.memory_manager.search(["cat"])
        self.assertEqual(len(memories), 1)

    def test_search_fuzzy_keyword(self):
        memories = self.memory_manager.search(["cat"], fuzzy_threshold=0.5)
        self.assertEqual(len(memories), 2)

        memories = self.memory_manager.search(["drive"], fuzzy_threshold=0.3)
        self.assertEqual(len(memories), 2)

    def test_load_same_memory_manager(self):
        same_memory_manager = MemoryChain.load(uuid=self.uuid)
        self.assertEqual(same_memory_manager.uuid, self.memory_manager.uuid)


if __name__ == "__main__":
    unittest.main()
