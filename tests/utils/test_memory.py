import datetime
import unittest

from banterbot.data.enums import ChatCompletionRoles
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message


class TestMemory(unittest.TestCase):
    """
    This test suite includes tests for the following:

        1. `test_memory_creation`: Tests that the `Memory` object is created with the correct attributes.
        2. `test_memory_equality`: Tests the equality magic method (`__eq__`) of the `Memory` class.
        3. `test_memory_to_protobuf`: Tests the conversion of a `Memory` object to a protobuf object.
        4. `test_memory_serialize_deserialize`: Tests the serialization and deserialization of a `Memory` object.
        5. `test_memory_from_protobuf`: Tests the construction of a `Memory` object from a protobuf object.

    The `setUp` method initializes a `Memory` object with sample data to be used in the tests.
    """

    def setUp(self):
        self.keywords: list[str] = ["keyword1", "keyword2", "keyword3"]
        self.summary: str = "This is a test memory summary."
        self.impact: int = 50
        self.timestamp: datetime.datetime = datetime.datetime.now()
        self.messages: list[Message] = [
            Message(role=ChatCompletionRoles.USER, content="User message 1"),
            Message(role=ChatCompletionRoles.ASSISTANT, content="Assistant message 1"),
            Message(role=ChatCompletionRoles.USER, content="User message 2"),
        ]
        self.memory = Memory(
            keywords=self.keywords,
            summary=self.summary,
            impact=self.impact,
            timestamp=self.timestamp,
            messages=self.messages,
        )

    def test_memory_creation(self):
        self.assertEqual(self.memory.keywords, self.keywords)
        self.assertEqual(self.memory.summary, self.summary)
        self.assertEqual(self.memory.impact, self.impact)
        self.assertEqual(self.memory.timestamp, self.timestamp.replace(microsecond=0))
        self.assertEqual(self.memory.messages, self.messages)

    def test_memory_equality(self):
        memory2 = Memory(
            keywords=self.keywords,
            summary=self.summary,
            impact=self.impact,
            timestamp=self.timestamp,
            messages=self.messages,
            uuid=self.memory.uuid,
        )
        self.assertEqual(self.memory, memory2)

    def test_memory_to_protobuf(self):
        memory_proto = self.memory.to_protobuf()
        self.assertEqual(memory_proto.keywords, self.keywords)
        self.assertEqual(memory_proto.summary, self.summary)
        self.assertEqual(memory_proto.impact, self.impact)
        self.assertEqual(memory_proto.timestamp, int(self.timestamp.timestamp()))
        self.assertEqual(len(memory_proto.messages), len(self.messages))
        self.assertEqual(memory_proto.uuid, self.memory.uuid)

    def test_memory_serialize_deserialize(self):
        serialized_memory = self.memory.serialize()
        deserialized_memory = Memory.deserialize(serialized_memory)
        self.assertEqual(self.memory, deserialized_memory)

    def test_memory_from_protobuf(self):
        memory_proto = self.memory.to_protobuf()
        memory_from_proto = Memory.from_protobuf(memory_proto)
        self.assertEqual(self.memory, memory_from_proto)


if __name__ == "__main__":
    unittest.main()
