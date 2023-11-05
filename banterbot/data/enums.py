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
    STYLEDEGREES = {"x-weak": 0.85, "weak": 0.95, "normal": 1.0, "strong": 1.05, "x-strong": 1.15}
    PITCHES = {"x-low": "-0.5%", "low": "-0.25%", "normal": "+0%", "high": "+0.25%", "x-high": "+0.5%"}
    RATES = {"x-slow": 0.85, "slow": 0.95, "normal": 1.0, "fast": 1.05, "x-fast": 1.15}
    EMPHASES = {"reduced": "reduced", "normal": "none", "exaggerated": "moderate"}


class ToneMode:
    """
    Different possible settings for tones in class `Interface`.
    """

    NONE = None
    BASIC = 1
    ADVANCED = 2
