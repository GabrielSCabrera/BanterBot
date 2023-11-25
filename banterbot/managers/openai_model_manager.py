from banterbot import paths
from banterbot.managers.resource_manager import ResourceManager
from banterbot.models.openai_model import OpenAIModel


class OpenAIModelManager:
    """
    Management utility for loading OpenAI ChatCompletion models from the resource JSON specified by
    `config.openai_models`. Only one instance per name is permitted to exist at a time, and loading occurs lazily,
    meaning that when a name is loaded, it is subsequently stored in cache and all future calls refer to the cached
    instance.
    """

    _data = {}

    @classmethod
    def list(cls) -> list[str]:
        """
        List the names of all the available OpenAI ChatCompletion models.

        Returns:
            list[str]: A list of names.
        """
        openai_models = ResourceManager.load_json(filename=paths.openai_models)
        return list(openai_models.keys())

    @classmethod
    def load(cls, name: str) -> OpenAIModel:
        """
        Retrieve or initialize an `OpenAIModel` instance by a name in the OpenAIModels resource JSON.

        Args:
            name (str): The name of the OpenAI ChatCompletion model.

        Returns:
            OpenAIModel: An `OpenAIModel` instance loaded with data from the specified name.

        Raises:
            KeyError: If the specified name is not found in the resource file defined by `config.openai_models`.
        """
        if name.lower() not in cls._data:
            openai_models = ResourceManager.load_json(filename=paths.openai_models)

            if name.lower() not in openai_models:
                available_models = ", ".join(f"`{name}`" for name in openai_models)
                message = (
                    f"BanterBot was unable to locate an OpenAI ChatCompletion model named: `{name}`, available models "
                    f"are: {available_models}."
                )
                raise KeyError(message)

            model_data = openai_models[name.lower()]
            model = OpenAIModel(
                model=model_data["model"],
                max_tokens=model_data["max_tokens"],
                generation=model_data["generation"],
                rank=model_data["rank"],
            )
            cls._data[name.lower()] = model

        return cls._data[name.lower()]
