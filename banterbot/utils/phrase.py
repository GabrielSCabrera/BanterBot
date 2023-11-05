from dataclasses import dataclass
from typing import Optional

from banterbot.data.azure_neural_voices import AzureNeuralVoice


@dataclass
class Phrase:
    """
    Contains processed data for a sub-sentence returned from a ChatCompletion ProsodySelection prompt, ready for
    SSML interpretation.
    """

    text: str
    style: Optional[str]
    styledegree: Optional[str]
    pitch: Optional[str]
    rate: Optional[str]
    emphasis: Optional[str]
    voice: AzureNeuralVoice
