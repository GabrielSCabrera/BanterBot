from pathlib import Path

# Environment variable names
OPENAI_API_KEY = "OPENAI_API_KEY"
AZURE_SPEECH_KEY = "AZURE_SPEECH_KEY"
AZURE_SPEECH_REGION = "AZURE_SPEECH_REGION"

# OpenAI API parameters
ASSISTANT = "assistant"
SYSTEM = "system"
USER = "user"
RETRY_LIMIT = 2

# Azure Neural Voice parameters
MALE = "male"
FEMALE = "female"

# SpaCy language models
EN_CORE_WEB_SM = "en_core_web_sm"
EN_CORE_WEB_MD = "en_core_web_md"

# The default seed to use in all random generation
SEED = 1337

# Initialize the filesystem for BanterBot
filesystem = Path.home() / "Documents" / "BanterBot"
filesystem.mkdir(parents=True, exist_ok=True)

# Initialize the chat log directory for BanterBot
chat_logs = filesystem / "Conversations"
chat_logs.mkdir(parents=True, exist_ok=True)
