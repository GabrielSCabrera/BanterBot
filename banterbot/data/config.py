from pathlib import Path

# Maximum number of retries in calls to the OpenAI API
RETRY_LIMIT = 2

# The default seed to use in all random generation
SEED = 1337

# Initialize the filesystem for BanterBot
filesystem = Path.home() / "Documents" / "BanterBot"
filesystem.mkdir(parents=True, exist_ok=True)

# Initialize the chat log directory for BanterBot
chat_logs = filesystem / "Conversations"
chat_logs.mkdir(parents=True, exist_ok=True)
