import datetime
from dataclasses import dataclass
from typing import Optional

from typing_extensions import Self

from banterbot import config

# File `memory_pb2.py` is automatically generated from protoc
from banterbot.protos import memory_pb2
from banterbot.utils.message import Message


@dataclass
class Memory:
    """
    This class represents a single memory of a persona in the form of a dataclass. A memory is defined by keywords, a
    summary, an impact score, a timestamp, and associated messages.

    Args:
        keywords (list[str]): The list of keywords that summarize the memory.
        summary (str): A brief summary of the memory.
        impact (float): A score to indicate the impact of the memory on the persona (accepts values 1 to 100).
        timestamp (datetime.datetime): The time when the memory occurred.
        messages (list[Message]): The list of messages associated with the memory.
    """

    keywords: list[str]
    summary: str
    impact: int
    timestamp: datetime.datetime
    messages: list[Message]
    uuid: Optional[str] = None

    def __post_init__(self):
        """
        Initializes a UUID for the current instance if one is not provided andtruncates microseconds from the provided
        timestamp.
        """
        if self.uuid is None:
            self.uuid = config.generate_uuid().hex
        self.timestamp = self.timestamp.replace(microsecond=0)

    def __eq__(self, memory: "Memory"):
        """
        Equality magic method, to allow equality checks between different instances of class `Memory` with the same
        contents.

        Args:
            memory (Memory): An instance of class Memory.
        """
        return (
            self.keywords == memory.keywords
            and self.summary == memory.summary
            and self.impact == memory.impact
            and self.timestamp == memory.timestamp
            and self.messages == memory.messages
            and self.uuid == memory.uuid
        )

    def to_protobuf(self) -> memory_pb2.Memory:
        """
        Converts this `Memory` instance into a protobuf object.
        Args:
            self: The instance of the `Memory` class.

        Returns:
            memory_pb2.Memory: The protobuf object equivalent of the `Memory` instance.
        """
        memory = memory_pb2.Memory()
        memory.keywords.extend(self.keywords)
        memory.summary = self.summary
        memory.impact = self.impact
        memory.timestamp = int(self.timestamp.timestamp())
        memory.messages.extend([message.to_protobuf() for message in self.messages])
        memory.uuid = self.uuid

        return memory

    def serialize(self) -> str:
        """
        Returns a serialized bytes string version of the current `Memory` instance.

        Returns:
            str: A string containing binary bytes.
        """
        return self.to_protobuf().SerializeToString()

    @classmethod
    def deserialize(cls, data: str) -> Self:
        """
        Constructs a `Memory` instance from a serialized string of binary bytes.

        Returns:
            Memory: The constructed `Memory` instance.
        """
        memory = memory_pb2.Memory()
        memory.ParseFromString(data)
        return cls.from_protobuf(memory=memory)

    @classmethod
    def from_protobuf(cls, memory: memory_pb2.Memory) -> "Memory":
        """
        Constructs a `Memory` instance from a protobuf object.

        Args:
            memory (memory_pb2.Memory): The protobuf object to convert.

        Returns:
            Memory: The constructed `Memory` instance.
        """
        # The `Memory` instance is created with the same attributes as the protobuf object.
        return cls(
            keywords=memory.keywords,
            summary=memory.summary,
            impact=memory.impact,
            timestamp=datetime.datetime.fromtimestamp(memory.timestamp),
            messages=[Message.from_protobuf(message_proto) for message_proto in memory.messages],
            uuid=memory.uuid,
        )
