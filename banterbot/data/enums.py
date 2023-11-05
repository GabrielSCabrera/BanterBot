from enum import Enum


class EnvVar(Enum):
    """
    Environment variables for API keys.
    """

    OPENAI_API_KEY = "OPENAI_API_KEY"
    AZURE_SPEECH_KEY = "AZURE_SPEECH_KEY"
    AZURE_SPEECH_REGION = "AZURE_SPEECH_REGION"


class ChatCompletionRoles(Enum):
    """
    Roles for the OpenAI ChatCompletion API.
    """

    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class WordCategory(Enum):
    """
    Word boundary categories for the Azure Speech API.
    """

    WORD = "word"
    PUNCTUATION = "punctuation"


class AzureNeuralVoiceGender(Enum):
    """
    Neural voice gender categories for the Azure Speech API.
    """

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class SpaCyLangModel(Enum):
    """
    Names of SpaCy languge models.
    """

    EN_CORE_WEB_SM = "en_core_web_sm"
    EN_CORE_WEB_MD = "en_core_web_md"
    EN_CORE_WEB_LG = "en_core_web_lg"


class SpeechProcessingType(Enum):
    """
    Speech processing category identifiers for the `Word` class.
    """

    TTS = "text-to-speech"
    STT = "speech-to-text"


class Prosody:
    """
    Prosody specifications for Azure Speech API SSML.
    Do not modify unless you know what you are doing -- changes would likely break `ProsodySelection` in data/prompts
    and method `prosody_prompt` in class AzureNeuralVoices, and everything dependent on these, in ways that are not
    immediately noticeable.
    """

    STYLES = [
        "angry",
        "cheerful",
        "excited",
        "friendly",
        "hopeful",
        "sad",
        "shouting",
        "terrified",
        "unfriendly",
        "whispering",
    ]
    STYLEDEGREES = ["x-weak", "weak", "default", "strong", "x-strong"]
    PITCHES = ["x-low", "low", "default", "high", "x-high"]
    RATES = ["x-slow", "slow", "default", "fast", "x-fast"]
    EMPHASES = ["reduced", "none", "moderate", "strong"]
