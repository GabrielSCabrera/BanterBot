from enum import Enum


class EnvVar(Enum):
    OPENAI_API_KEY = "OPENAI_API_KEY"
    AZURE_SPEECH_KEY = "AZURE_SPEECH_KEY"
    AZURE_SPEECH_REGION = "AZURE_SPEECH_REGION"


class ChatCompletionRoles(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class WordCategory(Enum):
    WORD = "word"
    PUNCTUATION = "punctuation"


class AzureNeuralVoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"


class SpaCyLangModel(Enum):
    EN_CORE_WEB_SM = "en_core_web_sm"
    EN_CORE_WEB_MD = "en_core_web_md"


class SpeechProcessingType(Enum):
    TTS = "text-to-speech"
    STT = "speech-to-text"
