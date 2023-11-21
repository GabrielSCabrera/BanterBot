from dataclasses import dataclass
from typing import Optional

from banterbot.data.enums import AzureNeuralVoiceGender


@dataclass
class AzureNeuralVoice:
    """
    A dataclass representing an Azure Neural Voice profile for speech synthesis.

    Attributes:
        name (str): The name of the voice profile.
        voice (str): The voice identifier used by Azure Text-to-Speech API.
        gender (AzureNeuralVoiceGender): The gender of the voice (either MALE or FEMALE).
        styles (list[str], optional): The available styles (i.e., tones/emotions) for the voice.
    """

    name: str
    voice: str
    gender: AzureNeuralVoiceGender
    styles: Optional[list[str]] = None
