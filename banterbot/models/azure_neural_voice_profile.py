from dataclasses import dataclass
from typing import Optional

from azure.cognitiveservices.speech import SynthesisVoiceGender


@dataclass
class AzureNeuralVoiceProfile:
    """
    A dataclass representing an Azure Neural Voice profile for speech synthesis.

    Attributes:
        country (str): The country where the voice is commonly used.
        description (str): A brief description of the voice profile.
        gender (SynthesisVoiceGender): The gender of the voice.
        language (str): The language of the voice.
        locale (str): The name of the language's locale (i.e., language-country[-region]).
        name (str): The name of the voice profile.
        region (str): The region where the voice is available or commonly used.
        short_name (str): The voice identifier used by Azure Text-to-Speech API.
        style_list (list[str]): The available styles (i.e., tones/emotions) for the voice.
    """

    country: str
    description: str
    gender: SynthesisVoiceGender
    language: str
    locale: str
    name: str
    short_name: str
    style_list: list[str]
    region: Optional[str] = None

    def __post_init__(self):
        if len(self.style_list) == 1 and not self.style_list[0].strip():
            self.style_list = []

    def __str__(self):
        styles = f"{', '.join(self.style_list)}" if self.style_list else "None"
        return (
            f"Azure Neural Voice Profile - {self.name}:\n"
            f"Locale: {self.locale}\n"
            f"Gender: {self.gender.name}\n"
            f"Styles: {styles}"
        )

    def __repr__(self):
        return (
            f"AzureNeuralVoice(country={self.country!r}, description={self.description!r}, "
            f"gender={self.gender!r}, language={self.language!r}, "
            f"locale={self.locale!r}, name={self.name!r}, region={self.region!r}, "
            f"short_name={self.short_name!r}, style_list={self.style_list!r})"
        )
