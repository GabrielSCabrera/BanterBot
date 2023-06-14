import bisect
from typing import List

from banterbot.protos import memory_pb2
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message


class Persona:
    def __init__(self, memories: List[Memory]):
        """
        Represents a persona consisting of memories.

        Args:
            memories (List[Memory]): List of Memory instances representing the memories of the persona.
        """
        self.memories = memories
        self.index = self.build_index()

    def save_memories(self):
        """
        Saves the memories to a binary file using Protocol Buffers serialization.
        """
        memory_list_proto = memory_pb2.MemoryList()

        for memory in self.memories:
            memory_proto = memory.to_protobuf()
            memory_list_proto.memories.append(memory_proto)

        serialized_memory_list = memory_list_proto.SerializeToString()

        try:
            with open("memories.bin", "wb") as f:
                f.write(serialized_memory_list)
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")

    def build_index(self):
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

    def load_memories(self):
        """
        Loads the memories from a binary file using Protocol Buffers deserialization.

        Returns:
            List[Memory]: List of loaded Memory instances.
        """
        memory_list_proto = memory_pb2.MemoryList()

        try:
            with open("memories.bin", "rb") as f:
                memory_list_proto.ParseFromString(f.read())
        except Exception as e:
            print(f"An error occurred while reading from the file: {e}")
            return []

        return [Memory.from_protobuf(memory_proto) for memory_proto in memory_list_proto.memories]

    def load(self, keywords: List[str]) -> List[Memory]:
        """
        Loads memories associated with the given keywords.

        Args:
            keywords (List[str]): List of keywords.

        Returns:
            List[Memory]: List of loaded Memory instances associated with the given keywords.
        """
        memories = self.load_memories()

        result = []
        for keyword in keywords:
            if keyword in self.index:
                for i in self.index[keyword]:
                    result.append(memories[i])
        return result
