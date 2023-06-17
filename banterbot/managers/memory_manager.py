import logging
from typing import List

from banterbot import config
from banterbot.protos import memory_pb2
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message


class MemoryManager:
    """
    MemoryManager is a class responsible for managing and handling arrays of memories using Protocol Buffers. It
    provides functionality to save memories to a binary file, load memories from a binary file, and retrieve memories
    based on keywords.
    """

    @classmethod
    def new(cls) -> "MemoryManager":
        """
        Generates a new empty set of memories and associated UUID.

        Returns:
            MemoryManager: A MemoryManager instance with the loaded memories.
        """
        uuid = config.generate_uuid().hex

        directory = config.personae / uuid / config.memories
        directory.mkdir(exist_ok=True, parents=True)

        memory_index = memory_pb2.MemoryIndex()
        with open(config.personae / uuid / config.memory_index, "wb+") as fs:
            fs.write(memory_index.SerializeToString())

        logging.debug(f"MemoryManager created new UUID: `{uuid}`")
        return cls(uuid=uuid, memory_index={})

    @classmethod
    def load(cls, uuid: str) -> "MemoryManager":
        """
        Loads the memories from a binary file using Protocol Buffers deserialization and creates a MemoryManager
        instance.

        Args:
            uuid (str): A string-typed UUID with which the current set of memories is associated.

        Returns:
            MemoryManager: A MemoryManager instance with the loaded memories.
        """
        logging.debug(f"MemoryManager loading UUID: `{uuid}`")
        memory_index_object = memory_pb2.MemoryIndex()

        with open(config.personae / uuid / config.memory_index, "rb") as fs:
            memory_index_object.ParseFromString(fs.read())

        memory_index = {entry.keyword: list(entry.memory_uuids) for entry in memory_index_object.entries}

        return cls(uuid, memory_index)

    def __init__(self, uuid: str, memory_index: List[Memory]) -> None:
        """
        Represents a manager for handling arrays of memories using Protocol Buffers.

        Args:
            uuid (str): A string-typed UUID with which the current set of memories is associated.
            memory_index (Dict[str, List[str]]): Index of keywords and the names of the files
        """
        logging.debug(f"MemoryManager initialized with UUID: `{uuid}`")
        self.uuid = uuid
        self._memory_index = memory_index
        self._find_memories()

    def append(self, memory: Memory) -> None:
        """
        Appends a new memory to the list of memories.

        Args:
            memory (Memory): A Memory instance to be appended.
        """
        self._memories[memory.uuid] = memory
        self._update_index(memory=memory)

    def extend(self, memories: List[Memory]) -> None:
        """
        Adds a list of new memories to the list of memories.

        Args:
            memories (List[Memory]): List of Memory instances to be appended.
        """
        for memory in memories:
            self.append(memory=memory)

    def _find_memories(self) -> None:
        directory = config.personae / self.uuid / config.memories
        self._memories = {path.stem: None for path in directory.glob("*" + config.protobuf_extension)}

    def _update_index(self, memory: Memory) -> None:
        for keyword in memory.keywords:
            if keyword not in self._memory_index.keys():
                self._memory_index[keyword] = [memory.uuid]
            else:
                self._memory_index[keyword].append(memory.uuid)

    def _load_memory(self, memory_uuid: str) -> None:
        memory_object = memory_pb2.Memory()
        with open(config.personae / self.uuid / config.memories / memory_uuid + config.protobuf_extension, "rb") as fs:
            memory_object.ParseFromString(fs.read())
        self._memories[memory_uuid] = Memory.from_protobuf(memory=memory_object)

    def keyword_lookup(self, keywords: List[str]) -> List[Memory]:
        memories = []
        for keyword in keywords:
            for memory_uuid in self._memory_index[keyword]:
                if self._memories[memory_uuid] is None:
                    self._load_memory(memory_uuid=memory_uuid)
                if self._memories[memory_uuid] not in memories:
                    memories.append(self._memories[memory_uuid])
        return memories
