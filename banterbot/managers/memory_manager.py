import bisect
import os
from typing import List

from banterbot.config import personae
from banterbot.protos import memory_pb2
from banterbot.utils import Memory, Message


class MemoryManager:
    """
    MemoryManager is a class responsible for managing and handling arrays of memories using Protocol Buffers. It
    provides functionality to save memories to a binary file, load memories from a binary file, and retrieve memories
    based on keywords.
    """

    def __init__(self, uuid: str, memories: List[Memory] = None):
        """
        Represents a manager for handling arrays of memories using Protocol Buffers.

        Args:
            uuid (str): A string-typed UUID with which the current set of memories is associated.
            memories (List[Memory], optional): List of Memory instances representing the memories. Defaults to None.
        """
        self.uuid = uuid
        self.memories = memories if memories is not None else []
        self.index = self._build_index()

    def append(self, memory: Memory, build_index: bool = True) -> None:
        """
        Appends a new memory to the list of memories.

        Args:
            memory (Memory): A Memory instance to be appended.
            build_index (bool): If True, rebuilds the memory index.
        """
        self.memories.append(memory)
        if build_index:
            self.index = self._build_index()

    def extend(self, memories: List[Memory], build_index: bool = True) -> None:
        """
        Adds a list of new memories to the list of memories.

        Args:
            memories (List[Memory], optional): List of Memory instances to be appended.
            build_index (bool): If True, rebuilds the memory index.
        """
        self.memories.extend(memories)
        if build_index:
            self.index = self._build_index()

    def save(self) -> None:
        """
        Saves the memories to a binary file using Protocol Buffers serialization.
        """
        memory_list_proto = memory_pb2.MemoryList()

        for memory in self.memories:
            memory_proto = memory.to_protobuf()
            memory_list_proto.memories.append(memory_proto)

        serialized_memory_list = memory_list_proto.SerializeToString()

        os.makedirs(self.uuid, exist_ok=True)
        with open(personae / self.uuid / "memories.bin", "wb") as f:
            f.write(serialized_memory_list)

    def _build_index(self) -> dict:
        """
        Builds an index of keywords to memory indices for efficient memory retrieval.

        Returns:
            dict: The index mapping keywords to memory indices.
        """
        index = {}
        for i, memory in enumerate(self.memories):
            for keyword in memory.keywords:
                if keyword not in index:
                    index[keyword] = []
                bisect.insort(index[keyword], i)
        return index

    @classmethod
    def load(cls, uuid: str) -> "MemoryManager":
        """
        Loads the memories from a binary file using Protocol Buffers deserialization and creates a MemoryManager instance.

        Args:
            uuid (str): A string-typed UUID with which the current set of memories is associated.

        Returns:
            MemoryManager: A MemoryManager instance with the loaded memories.
        """
        memory_list_proto = memory_pb2.MemoryList()

        with open(personae / self.uuid / "memories.bin", "rb") as f:
            memory_list_proto.ParseFromString(f.read())

        memories = [Memory.from_protobuf(memory_proto) for memory_proto in memory_list_proto.memories]
        return cls(uuid, memories)

    def retrieve(self, keywords: List[str]) -> List[Memory]:
        """
        Retrieves memories associated with the given keywords.

        Args:
            keywords (List[str]): List of keywords.

        Returns:
            List[Memory]: List of retrieved Memory instances associated with the given keywords.
        """
        result = []
        for keyword in keywords:
            if keyword in self.index:
                for i in self.index[keyword]:
                    result.append(self.memories[i])
        return result
