from pathlib import Path

# Initialize the filesystem for BanterBot
filesystem = Path.home() / "Documents" / "BanterBot"
filesystem.mkdir(parents=True, exist_ok=True)

# Initialize the chat log directory
chat_logs = filesystem / "Conversations"
chat_logs.mkdir(parents=True, exist_ok=True)

# Initialize the personae memory and personality storage
personae = filesystem / "Personae"
personae.mkdir(parents=True, exist_ok=True)

# The name of the resource file containing OpenAI ChatCompletion models.
openai_models = "openai_models.json"
# The file that contains all data for primary traits.
primary_traits = "primary_traits.json"

# The extension that should be used in saving protocol buffers to file
protobuf_extension = ".bin"
# The name of the file in which to index memories by keyword
memory_index = "memory_index" + protobuf_extension
# The name of the directory in which memories should be saved
memories = "memories"
