import datetime
import logging
from pathlib import Path

import uuid6

# Maximum number of retries in calls to the OpenAI API
RETRY_LIMIT = 3

# The number of seconds to wait if the OpenAI API raises a RateLimitError
RETRY_TIME = 60

# The default seed to use in all random generation
SEED = 1337

# The default language used in speech-to-text recognition
DEFAULT_LANGUAGE = "en-US"

# Initialize the filesystem for BanterBot
filesystem = Path.home() / "Documents" / "BanterBot"
filesystem.mkdir(parents=True, exist_ok=True)

# Initialize the chat log directory
chat_logs = filesystem / "Conversations"
chat_logs.mkdir(parents=True, exist_ok=True)

# Initialize the personae memory and personality storage
personae = filesystem / "Personae"
personae.mkdir(parents=True, exist_ok=True)

# The name of the directory in which memories should be saved
memories = "memories"

# The name of the resource file containing Microsoft Azure Cognitive Speech Services Neural Voices.
azure_neural_voices = "azure_neural_voices.json"

# The name of the resource file containing OpenAI ChatCompletion models.
openai_models = "openai_models.json"

# The extension that should be used in saving protocol buffers to file
protobuf_extension = ".bin"

# The name of the file in which to index memories by keyword
memory_index = "memory_index" + protobuf_extension

# Set the log settings
logging_level = logging.INFO
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging_level)

# Define the type of UUID that should be used across all modules
generate_uuid = uuid6.uuid8

# Define the punctuation marks that can be used to split sentences into phrases for prosody selection.
phrase_delim = [",", ".", "?", "!", ":", ";", '"', "`", "|", "\n"]

# The amount of time that should be added to a "soft interruption" as defined in class `SpeechToText`.
soft_interruption_delay: datetime.timedelta = datetime.timedelta(seconds=0.5)
