from dataclasses import dataclass
from typing import List

# File `memory_pb2.py` is automatically generated from protoc
from banterbot.protos import memory_pb2
from banterbot.utils import Message


@dataclass
class Memory:
    """
    This class represents a single memory of a persona in the form of a dataclass.
    A memory is defined by keywords, a summary, an impact score, a timestamp,
    and associated messages.

    Args:
        keywords (List[str]): The list of keywords that summarize the memory.
        summary (str): A brief summary of the memory.
        impact (float): A score to indicate the impact of the memory on the persona.
        timestamp (str): The time when the memory occurred.
        messages (List[Message]): The list of messages associated with the memory.
    """

    keywords: List[str]
    summary: str
    impact: float
    timestamp: str
    messages: List[Message]

    def to_protobuf(self) -> memory_pb2.Memory:
        """
        Converts this Memory instance into a protobuf object.
        Args:
            self: The instance of the Memory class.

        Returns:
            memory_pb2.Memory: The protobuf object equivalent of the Memory instance.
        """
        # The protobuf object is generated with the same attributes as the Memory instance.
        return memory_pb2.Memory(
            keywords=self.keywords,
            summary=self.summary,
            impact=self.impact,
            timestamp=self.timestamp,
            messages=[message.to_protobuf() for message in self.messages],
        )

    @classmethod
    def from_protobuf(cls, memory: memory_pb2.Memory) -> "Memory":
        """
        Constructs a Memory instance from a protobuf object.

        Args:
            memory (memory_pb2.Memory): The protobuf object to convert.

        Returns:
            Memory: The constructed Memory instance.
        """
        # The Memory instance is created with the same attributes as the protobuf object.
        return cls(
            keywords=memory.keywords,
            summary=memory.summary,
            impact=memory.impact,
            timestamp=memory.timestamp,
            messages=[Message.from_protobuf(message_proto) for message_proto in memory.messages],
        )
