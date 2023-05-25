"""
An overview of Azure Neural Voice models for speech synthesis. Each voice profile is represented by an instance of the
`AzureNeuralVoice` dataclass, which provides the following information:

Attributes:
    name (str): The name of the voice profile.
    voice (str): The voice identifier.
    gender (Literal[MALE, FEMALE]): The gender of the voice (either MALE or FEMALE).
    pitch (int): The relative (by gender) pitch level of the voice, where a lower value indicates a lower pitch.
    styles (List[str]): The available styles (i.e., tones/emotions) for the voice.
"""
from dataclasses import dataclass
from typing import Literal

from banterbot.data.constants import FEMALE, MALE


@dataclass
class AzureNeuralVoice:
    name: str
    voice: str
    gender: Literal[MALE, FEMALE]
    pitch: int
    styles: list[str, ...]


# Available voice profiles
neural_voices = {
    "Aria": {
        "gender": FEMALE,
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
        "gender": MALE,
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
        "gender": MALE,
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
        "gender": FEMALE,
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
        "gender": MALE,
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
        "gender": FEMALE,
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
        "gender": FEMALE,
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
        "gender": FEMALE,
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
        "gender": MALE,
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
neural_voices = {name: AzureNeuralVoice(name=name, **voice) for name, voice in neural_voices.items()}
