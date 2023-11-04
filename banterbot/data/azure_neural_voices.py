"""
This program defines a dataclass and utility functions to represent and manage Azure Neural Voice profiles for speech
synthesis. The main components of the program are:

    1.  AzureNeuralVoice dataclass: Represents an Azure Neural Voice profile with attributes such as name, voice
        identifier, gender, pitch, and available styles (tones/emotions).

    2.  _neural_voices: A dictionary containing instances of AzureNeuralVoice for each available voice profile.

    3.  get_voice_by_name(name: str) -> AzureNeuralVoice: Retrieves an AzureNeuralVoice instance by its name.

The purpose of this program is to provide an organized and easily accessible representation of Azure Neural Voice
profiles for speech synthesis. Users can utilize the provided data and utility functions to easily retrieve voice
profiles based on their requirements (e.g., gender, pitch, or available styles).
"""

from dataclasses import dataclass
from typing import List, Optional

from banterbot.data.enums import AzureNeuralVoiceGender


@dataclass
class AzureNeuralVoice:
    """
    A dataclass representing an Azure Neural Voice profile for speech synthesis.

    Attributes:
        name (str): The name of the voice profile.
        voice (str): The voice identifier used by Azure Text-to-Speech API.
        gender (AzureNeuralVoiceGender): The gender of the voice (either MALE or FEMALE).
        pitch (int): The relative (by gender) pitch level of the voice, where a lower value indicates a lower pitch.
        styles (List[str], optional): The available styles (i.e., tones/emotions) for the voice.
    """

    name: str
    voice: str
    gender: AzureNeuralVoiceGender
    pitch: int
    styles: Optional[List[str]]


# Dictionary containing voice profile data
_neural_voice_data = {
    "Mattias": {
        "gender": AzureNeuralVoiceGender.MALE,
        "pitch": 2,
        "voice": "sv-SE-MattiasNeural",
        "styles": None,
    },
    "Aria": {
        "gender": AzureNeuralVoiceGender.FEMALE,
        "pitch": 3,
        "voice": "en-US-AriaNeural",
        "styles": [
            "angry",
            "chat",
            "cheerful",
            "customerservice",
            "empathetic",
            "excited",
            "friendly",
            "hopeful",
            "narration-professional",
            "newscast-casual",
            "newscast-formal",
            "sad",
            "shouting",
            "terrified",
            "unfriendly",
            "whispering",
        ],
    },
    "Davis": {
        "gender": AzureNeuralVoiceGender.MALE,
        "pitch": 0,
        "voice": "en-US-DavisNeural",
        "styles": [
            "angry",
            "chat",
            "cheerful",
            "excited",
            "friendly",
            "hopeful",
            "sad",
            "shouting",
            "terrified",
            "unfriendly",
            "whispering",
        ],
    },
    "Guy": {
        "gender": AzureNeuralVoiceGender.MALE,
        "pitch": 3,
        "voice": "en-US-GuyNeural",
        "styles": [
            "angry",
            "cheerful",
            "excited",
            "friendly",
            "hopeful",
            "newscast",
            "sad",
            "shouting",
            "terrified",
            "unfriendly",
            "whispering",
        ],
    },
    "Jane": {
        "gender": AzureNeuralVoiceGender.FEMALE,
        "pitch": 4,
        "voice": "en-US-JaneNeural",
        "styles": [
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
        ],
    },
    "Jason": {
        "gender": AzureNeuralVoiceGender.MALE,
        "pitch": 2,
        "voice": "en-US-JasonNeural",
        "styles": [
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
        ],
    },
    "Jenny": {
        "gender": AzureNeuralVoiceGender.FEMALE,
        "pitch": 0,
        "voice": "en-US-JennyNeural",
        "styles": [
            "angry",
            "assistant",
            "chat",
            "cheerful",
            "customerservice",
            "excited",
            "friendly",
            "hopeful",
            "newscast",
            "sad",
            "shouting",
            "terrified",
            "unfriendly",
            "whispering",
        ],
    },
    "Nancy": {
        "gender": AzureNeuralVoiceGender.FEMALE,
        "pitch": 2,
        "voice": "en-US-NancyNeural",
        "styles": [
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
        ],
    },
    "Sara": {
        "gender": AzureNeuralVoiceGender.FEMALE,
        "pitch": 1,
        "voice": "en-US-SaraNeural",
        "styles": [
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
        ],
    },
    "Tony": {
        "gender": AzureNeuralVoiceGender.MALE,
        "pitch": 1,
        "voice": "en-US-TonyNeural",
        "styles": [
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
        ],
    },
}

# Create instances of AzureNeuralVoice for each voice in the dictionary
_neural_voices = {name.lower(): AzureNeuralVoice(name=name, **voice) for name, voice in _neural_voice_data.items()}


def get_voice_by_name(name: str) -> AzureNeuralVoice:
    """
    Retrieve an AzureNeuralVoice instance by its name.

    Args:
        name (str): The name of the voice profile.

    Returns:
        AzureNeuralVoice: The corresponding AzureNeuralVoice instance.

    Raises:
        KeyError: If the specified name is not found in the _neural_voices dictionary.
    """
    if name.lower() not in _neural_voices.keys():
        available_voices = ", ".join(f"`{name}`" for name in _neural_voices.keys())
        error_message = (
            f"BanterBot was unable to load a Microsoft Azure neural voice model with the name `{name}`, available "
            f"voices are: {available_voices}."
        )
        raise KeyError(error_message)

    return _neural_voices[name.lower()]
