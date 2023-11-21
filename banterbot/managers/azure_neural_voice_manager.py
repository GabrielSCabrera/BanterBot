from banterbot import config
from banterbot.data.enums import AzureNeuralVoiceGender
from banterbot.managers.resource_manager import ResourceManager
from banterbot.models.azure_neural_voice import AzureNeuralVoice


class AzureNeuralVoiceManager:
    """
    Management utility for loading Microsoft Azure Cognitive Speech Services Neural Voice models from the resource JSON
    specified by `config.azure_neural_voices`. Only one instance per name is permitted to exist at a time, and loading
    occurs lazily, meaning that when a name is loaded, it is subsequently stored in cache and all future calls refer to
    the cached instance.
    """

    _data = {}

    @classmethod
    def list(cls) -> list[str]:
        """
        List the names of all the available Microsoft Azure Cognitive Speech Services Neural Voice models .

        Returns:
            list[str]: A list of names.
        """
        azure_neural_voices = ResourceManager.load_json(filename=config.azure_neural_voices)
        return list(azure_neural_voices.keys())

    @classmethod
    def load(cls, name: str) -> AzureNeuralVoice:
        """
        Retrieve or initialize an `AzureNeuralVoice` instance by a name in the Neural Voices resource JSON.

        Args:
            name (str): The name of the voice profile.

        Returns:
            AzureNeuralVoice: An `AzureNeuralVoice` instance loaded with data from the specified name.

        Raises:
            KeyError: If the specified name is not found in the resource file defined by `config.azure_neural_voices`.
        """
        if name.lower() not in cls._data:
            azure_neural_voices = ResourceManager.load_json(filename=config.azure_neural_voices)

            if name.lower() not in azure_neural_voices:
                available_voices = ", ".join(f"`{name}`" for name in azure_neural_voices)
                message = (
                    f"BanterBot was unable to locate a Microsoft Azure Cognitive Speech Services Neural Voice model "
                    f"named: `{name}`, available voices are: {available_voices}."
                )
                raise KeyError(message)

            voice_data = azure_neural_voices[name.lower()]
            voice = AzureNeuralVoice(
                name=name,
                voice=voice_data["voice"],
                gender=AzureNeuralVoiceGender[voice_data["gender"]],
                styles=voice_data["styles"],
            )
            cls._data[name.lower()] = voice

        return cls._data[name.lower()]
