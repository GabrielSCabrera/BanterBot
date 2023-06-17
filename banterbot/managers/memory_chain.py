import logging
from typing import Dict, List, Optional

from banterbot import config
from banterbot.data.enums import SpaCyLangModel
from banterbot.protos import memory_pb2
from banterbot.utils.memory import Memory
from banterbot.utils.message import Message
from banterbot.utils.nlp import NLP


class MemoryChain:
    """
    MemoryChain is a class responsible for managing and handling arrays of memories using Protocol Buffers. It provides
    functionality to save memories to a binary file, load memories from a binary file, and retrieve memories based on
    keywords. The MemoryChain class is designed to efficiently store and retrieve memories based on keywords, allowing
    for quick access to relevant information.
    """

    @classmethod
    def create(cls) -> "MemoryChain":
        """
        Generate a new empty set of memories and associated UUID.

        Returns:
            MemoryChain: A new instance of MemoryChain with an empty set of memories and a unique UUID.
        """
        uuid = config.generate_uuid().hex

        # Create new directory for the new UUID and memory files
        directory = config.personae / uuid / config.memories
        directory.mkdir(exist_ok=True, parents=True)

        # Create new memory index file
        memory_index = memory_pb2.MemoryIndex()
        with open(config.personae / uuid / config.memory_index, "wb+") as fs:
            fs.write(memory_index.SerializeToString())

        logging.debug(f"MemoryChain created new UUID: `{uuid}`")
        return cls(uuid=uuid, memory_index={})

    @classmethod
    def load(cls, uuid: str) -> "MemoryChain":
        """
        Load the memories from a binary file using Protocol Buffers deserialization and creates a MemoryChain instance.
        This method is used to load an existing set of memories from a file, allowing for the continuation of a previous
        session or the sharing of memories between different instances.

        Args:
            uuid (str): The UUID of the memory files to load.

        Returns:
            MemoryChain: A new instance of MemoryChain with loaded memories.
        """
        logging.debug(f"MemoryChain loading UUID: `{uuid}`")

        # Read memory index file
        memory_index_object = memory_pb2.MemoryIndex()
        with open(config.personae / uuid / config.memory_index, "rb") as fs:
            memory_index_object.ParseFromString(fs.read())

        # Parse the memory index file into a dictionary
        memory_index = {entry.keyword: list(entry.memory_uuids) for entry in memory_index_object.entries}

        return cls(uuid, memory_index)

    def __init__(self, uuid: str, memory_index: Dict[str, List[str]]) -> None:
        """
        Initialize a new instance of MemoryChain.

        Args:
            uuid (str): The UUID associated with this set of memories.

            memory_index (Dict[str, List[str]]): The dictionary mapping from keyword to list of memory UUIDs. This index
            is used to efficiently look up memories based on keywords.
        """
        logging.debug(f"MemoryChain initialized with UUID: `{uuid}`")
        self.uuid = uuid
        self._index_cache = memory_index
        self._memories = {}
        self._similarity_cache = {}
        self._token_cache = {}
        self._update_token_cache(self._index_cache.keys())
        self._find_memories()

    def append(self, memory: Memory) -> None:
        """
        Append a memory to the current set of memories. This method is used to add a single memory to the MemoryChain,
        allowing for the storage of new information. All changes are saved to file as soon as they are made.

        Args:
            memory (Memory): The memory to append.
        """
        self._memories[memory.uuid] = memory
        self._save_memory(memory=memory)
        self._update_index(memory=memory)
        self._save_index()

    def extend(self, memories: List[Memory]) -> None:
        """
        Extend the current set of memories with a list of memories. This method is used to add multiple memories to the
        MemoryChain at once, allowing for the storage of new information in bulk. All changes are saved to file as soon
        as they are made.

        Args:
            memories (List[Memory]): The list of memories to append.
        """
        for memory in memories:
            self._memories[memory.uuid] = memory
            self._save_memory(memory=memory)
            self._update_index(memory=memory)
        self._save_index()

    def search(self, keywords: List[str], fuzzy_threshold: Optional[float] = None) -> List[Memory]:
        """
        Look up memories based on keywords. This method is used to retrieve memories that are relevant to the given
        keywords. It can also perform fuzzy matching, allowing for the retrieval of memories that are similar to the
        given keywords based on a similarity threshold.

        Args:
            keywords (List[str]): The list of keywords to look up.

            fuzzy_threshold (Optional[float]): The threshold for fuzzy matching. If None, only returns exact matches. If
            a value is provided, memories with keywords that have a similarity score greater than or equal to the
            threshold will also be returned.

        Returns:
            List[Memory]: The list of matching memories.
        """
        memory_uuids = set()
        memories = []
        if fuzzy_threshold is not None:
            self._update_similarity_cache(keywords=keywords)

            # Find additional keywords that are similar to the given keywords
            keywords_extension = []
            cache_filtered = [i for i in self._index_cache.keys() if i not in keywords]
            for keyword in keywords:
                for keyword_indexed in cache_filtered:
                    if self._similarity_cache[(keyword, keyword_indexed)] >= fuzzy_threshold:
                        keywords_extension.append(keyword_indexed)
            keywords.extend(keywords_extension)

        # Add memory UUIDs to the result set
        for keyword in keywords:
            if keyword in self._index_cache.keys():
                for memory_uuid in self._index_cache[keyword]:
                    if self._memories[memory_uuid] is None:
                        self._load_memory(memory_uuid=memory_uuid)
                    memory_uuids.add(memory_uuid)

        # Write all the Memory objects into a list
        for memory_uuid in memory_uuids:
            memories.append(self._memories[memory_uuid])

        return memories

    def _save_memory(self, memory: Memory) -> None:
        """
        Save an instance of class Memory to file using protocol buffers.
        """
        filename = memory.uuid + config.protobuf_extension
        with open(config.personae / self.uuid / config.memories / filename, "wb+") as fs:
            fs.write(memory.serialize())

    def _save_index(self) -> None:
        """
        Save the current state of the memory index to file.
        """
        memory_index = memory_pb2.MemoryIndex()
        for keyword, memory_uuids in self._index_cache.items():
            memory_index_entry = memory_pb2.MemoryIndexEntry()
            memory_index_entry.keyword = keyword
            memory_index_entry.memory_uuids.extend(memory_uuids)
            memory_index.entries.append(memory_index_entry)

        with open(config.personae / self.uuid / config.memory_index, "wb+") as fs:
            fs.write(memory_index.SerializeToString())

    def _find_memories(self) -> None:
        """
        Find all memory files associated with this UUID and store them in _memories dictionary. This method is used to
        locate all memory files that belong to the current MemoryChain instance, allowing for the efficient loading and
        retrieval of memories when needed.
        """
        directory = config.personae / self.uuid / config.memories
        self._memories = {path.stem: None for path in directory.glob("*" + config.protobuf_extension)}

    def _update_index(self, memory: Memory) -> None:
        """
        Update the memory index with a new memory. This method is used to keep the memory index up-to-date when new
        memories are added to the MemoryChain. The index allows for efficient look-up of memories based on keywords.

        Args:
            memory (Memory): The memory to update the index with.
        """
        for keyword in memory.keywords:
            if keyword not in self._index_cache.keys():
                self._index_cache[keyword] = set()
            self._index_cache[keyword].add(memory.uuid)
        self._update_token_cache(memory.keywords)

    def _load_memory(self, memory_uuid: str) -> None:
        """
        Load a memory from a memory file. This method is used to load a specific memory from a file when it is needed,
        allowing for efficient memory usage by only loading memories when they are required.

        Args:
            memory_uuid (str): The UUID of the memory to load.
        """
        filename = memory_uuid + config.protobuf_extension
        with open(config.personae / self.uuid / config.memories / filename, "rb") as fs:
            self._memories[memory_uuid] = Memory.deserialize(fs.read())

    def _update_token_cache(self, keywords: List[str]) -> None:
        """
        Update the token cache with new keywords. This method is used to keep the token cache up-to-date when new
        keywords are added to the MemoryChain. The token cache allows for efficient computation of similarity scores
        between keywords.

        Args:
            keywords (List[str]): The new keywords to update the cache with.
        """
        new_keywords = [keyword for keyword in keywords if keyword not in self._token_cache.keys()]
        for keyword, token in zip(new_keywords, NLP.tokenize(strings=new_keywords)):
            self._token_cache[keyword] = token

    def _update_similarity_cache(self, keywords: List[str]) -> None:
        """
        Update the similarity cache with new keywords. This method is used to keep the similarity cache up-to-date when
        new keywords are added to the MemoryChain. The similarity cache allows for efficient computation of similarity
        scores between keywords, enabling fuzzy matching in the search method.

        Args:
            keywords (List[str]): The new keywords to update the cache with.
        """
        self._update_token_cache(keywords=keywords)
        for keyword_indexed in self._index_cache.keys():
            for keyword in keywords:
                pair = (keyword, keyword_indexed)
                if pair not in self._similarity_cache.keys():
                    similarity = self._token_cache[keyword].similarity(self._token_cache[keyword_indexed])
                    self._similarity_cache[pair] = similarity
