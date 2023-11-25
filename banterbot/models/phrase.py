from dataclasses import dataclass
from typing import Optional

from banterbot.models.azure_neural_voice_profile import AzureNeuralVoiceProfile


@dataclass
class Phrase:
    """
    Contains processed data for a sub-sentence returned from a ChatCompletion ProsodySelection prompt, ready for SSML
    interpretation.
    """

    text: str
    voice: AzureNeuralVoiceProfile
    style: Optional[str] = None
    styledegree: Optional[str] = None
    pitch: Optional[str] = None
    rate: Optional[str] = None
    emphasis: Optional[str] = None
