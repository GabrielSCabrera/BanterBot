import unittest
import datetime
from banterbot.data.enums import ChatCompletionRoles
from banterbot.managers.memory_chain import MemoryChain
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message

class TestMemoryChain(unittest.TestCase):
    def setUp(self):
        self.memory_manager = MemoryChain.create()
        self.uuid = self.memory_manager.uuid
        msg1 = Message(ChatCompletionRoles.ASSISTANT, "Hello")
        msg2 = Message(ChatCompletionRoles.ASSISTANT, "Hi")
        msg3 = Message(ChatCompletionRoles.ASSISTANT, "How are you?")
        memory = Memory(["dog", "cat"], "memory1 summary", 60, datetime.datetime.now(), [msg1, msg2])
        self.memory_manager.append(memory)
        memories = [
            Memory(["car", "feline"], "memory2 summary", 80, datetime.datetime.now(), [msg2]),
            Memory(["eat", "drive"], "memory3 summary", 70, datetime.datetime.now(), [msg1, msg3]),
        ]
        self.memory_manager.extend(memories)

    def test_search_exact(self):
        memories = self.memory_manager.search(["cat"])
        self.assertEqual(len(memories), 1)

    def test_search_fuzzy(self):
        memories = self.memory_manager.search(["cat"], fuzzy_threshold=0.5)
        self.assertEqual(len(memories), 2)

    def test_search_fuzzy_threshold(self):
        memories = self.memory_manager.search(["drive"], fuzzy_threshold=0.3)
        self.assertEqual(len(memories), 2)

    def test_load_and_search(self):
        loaded_memory_manager = MemoryChain.load(uuid=self.uuid)

        memories = loaded_memory_manager.search(["cat"])
        self.assertEqual(len(memories), 1)

        memories_fuzzy = loaded_memory_manager.search(["cat"], fuzzy_threshold=0.5)
        self.assertEqual(len(memories_fuzzy), 2)

        memories_fuzzy_threshold = loaded_memory_manager.search(["drive"], fuzzy_threshold=0.3)
        self.assertEqual(len(memories_fuzzy_threshold), 2)

        self.assertEqual(loaded_memory_manager.uuid, self.memory_manager.uuid)

if __name__ == "__main__":
    unittest.main()
