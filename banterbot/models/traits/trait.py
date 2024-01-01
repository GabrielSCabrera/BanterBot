from banterbot.managers.resource_manager import ResourceManager


class Trait:
    """
    A superclass for traits, with shared methods for loading, visualizing, and managing data.
    """

    def __init__(self, uuid: str, name: str, description: str, value: int, value_description: str):
        """
        Initialize a Trait instance.

        Args:
            uuid (str): The unique identifier of the trait.
            name (str): The name of the trait.
            description (str): A textual description of the trait.
            value (int): The specific value of the trait.
            value_description (str): Description of the trait at the specified value.
        """
        self.uuid = uuid
        self.name = name
        self.description = description
        self.value = value
        self.value_description = value_description

    def __str__(self):
        return f"{self.__class__.__name__} {self.name}: {self.value_description}"

    def __repr__(self):
        output = (
            f"<class '{self.__class__.__name__}' | UUID `{self.uuid}` | Name `{self.name}` | Value `{self.value}` |"
            f" Value Description `{self.value_description}`>"
        )
        return output

    @classmethod
    def _load_uuid(cls, uuid: str, resource: str) -> dict:
        """
        Helper method to load trait data from the specified JSON based on UUID.

        Args:
            uuid (str): The UUID of the trait.
            resource (str): The resource to load the trait data from.

        Returns:
            dict: The data for the specified trait.
        """
        traits_data = ResourceManager.load_json(resource=resource, cache=True, reset=False)

        # Search for the trait data based on UUID
        if uuid in traits_data:
            return traits_data[uuid]
        else:
            message = f"The specified UUID `{uuid}` does not exist in `resources/{resource}`"
            raise KeyError(message)
