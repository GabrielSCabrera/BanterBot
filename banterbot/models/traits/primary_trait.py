import random

from typing_extensions import Self

from banterbot.managers.resource_manager import ResourceManager
from banterbot.paths import primary_traits


class PrimaryTrait:
    """
    Primary trait loading and management, with options for random generation or specified parameters using data from the
    `paths.primary_traits` resource.
    """

    def __init__(self, name: str, description: str, value: int, value_description: str):
        """
        Initialize a PrimaryTrait instance.

        Args:
            name (str): The name of the primary trait.
            description (str): A textual description of the primary trait.
            value (int): The specific value of the primary trait.
            value_description (str): Description of the trait at the specific value.
        """
        self.name = name
        self.description = description
        self.value = value
        self.value_description = value_description

    def __str__(self):
        return f"{self.name} (Value: {self.value}): {self.value_description}"

    @classmethod
    def load_random(cls, uuid: str) -> Self:
        """
        Load a PrimaryTrait instance based on a UUID with a randomly selected value.

        Args:
            uuid (str): The unique identifier of the primary trait.

        Returns:
            PrimaryTrait: An instance of PrimaryTrait with a randomly selected value.
        """
        data = cls._load_uuid(uuid)

        value = random.randrange(len(data["levels"]))

        value_description = data["levels"][value]
        return cls(data["name"], data["description"], value, value_description)

    @classmethod
    def load_select(cls, uuid: str, value: int) -> Self:
        """
        Load a PrimaryTrait instance based on a UUID with a specified value.

        Args:
            uuid (str): The unique identifier of the primary trait.
            value (int): The specified value for the trait.

        Returns:
            PrimaryTrait: An instance of PrimaryTrait with the specified value.
        """
        data = cls._load_uuid(uuid)

        if not isinstance(value, int) or 0 > value >= len(data["levels"]):
            raise ValueError("Specified value is out of the valid range for this trait.")

        value_description = data["levels"][value - data["range"][0]]
        return cls(data["name"], data["description"], value, value_description)

    @classmethod
    def _load_uuid(cls, uuid: str):
        """
        Helper method to load trait data from the `primary_traits` JSON based on UUID.

        Args:
            uuid (str): The UUID of the trait.

        Returns:
            dict: The data for the specified trait.
        """
        traits_data = ResourceManager.load_json(filename=primary_traits, cache=True, reset=False)

        # Search for the trait data based on UUID
        if uuid in traits_data["primary_traits"]:
            return traits_data["primary_traits"][uuid]
        else:
            message = f"The specified UUID `{uuid}` is not a known Primary Trait in `resources/{primary_traits}`"
            raise KeyError(message)
