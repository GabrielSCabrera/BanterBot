import datetime
from dataclasses import dataclass
from typing import List, Optional

from banterbot import config

# File `memory_pb2.py` is automatically generated from protoc
from banterbot.protos import memory_pb2
from banterbot.utils.message import Message


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
    timestamp: datetime.datetime
    messages: List[Message]
    uuid: Optional[str] = None

    def __post_init__(self):
        """
        Initializes a UUID for the current instance if one is not provided.
        """
        if self.uuid is None:
            self.uuid = config.generate_uuid().hex

    def to_protobuf(self) -> memory_pb2.Memory:
        """
        Converts this Memory instance into a protobuf object.
        Args:
            self: The instance of the Memory class.

        Returns:
            memory_pb2.Memory: The protobuf object equivalent of the Memory instance.
        """
        memory = memory_pb2.Memory()

        memory.keywords.extend(self.keywords)
        memory.summary = self.summary
        memory.impact = self.impact
        memory.timestamp = self.timestamp.timestamp()
        memory.messages.extend([message.to_protobuf() for message in self.messages])
        memory.uuid = self.uuid

        return memory

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
            timestamp=datetime.datetime.fromtimestamp(memory.timestamp),
            messages=[Message.from_protobuf(message_proto) for message_proto in memory.messages],
            uuid=memory.uuid,
        )
