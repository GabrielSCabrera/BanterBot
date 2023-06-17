from banterbot import config
from banterbot.managers.memory_manager import MemoryManager

memory_manager = MemoryManager.new()
uuid = memory_manager.uuid

memory_manager = MemoryManager.load(uuid=uuid)
print(memory_manager.memory_index)
