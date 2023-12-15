from dataclasses import dataclass

from banterbot.models.azure_neural_voice_profile import AzureNeuralVoiceProfile


@dataclass
class Phrase:
    """
    Contains processed data for a sub-sentence returned from a ChatCompletion ProsodySelection prompt, ready for SSML
    interpretation.
    """

    text: str
    voice: AzureNeuralVoiceProfile
    style: str = ""
    styledegree: str = ""
    pitch: str = ""
    rate: str = ""
    emphasis: str = ""
