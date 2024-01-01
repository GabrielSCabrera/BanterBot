import random
from typing import Union

from typing_extensions import Self

from banterbot.models.traits.trait import Trait


class PrimaryTrait(Trait):
    """
    Primary trait loading and management, with options for random generation or specified parameters using data from the
    `resources.primary_traits` resource.

    Attributes:
        uuid (str): The unique identifier for the trait.
        name (str): The name of the trait.
        description (str): The description of the trait.
        value (int): The value of the trait.
        value_description (str): The description of the trait value.
    """

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

        return cls(
            uuid=uuid,
            name=data["name"],
            description=data["description"],
            value=value,
            value_description=data["levels"][value],
        )

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
            raise ValueError(f"Specified value `{value}` is out of the valid range for trait `{uuid}`.")

        return cls(
            uuid=uuid,
            name=data["name"],
            description=data["description"],
            value=value,
            value_description=data["levels"][value],
        )

    @classmethod
    def _load_uuid(cls, uuid: str) -> dict[str, dict[str, Union[str, list[str]]]]:
        """
        Helper method to load trait data from the `primary_traits` JSON based on UUID.

        Args:
            uuid (str): The UUID of the primary trait.

        Returns:
            dict[str, dict[str, Union[str, list[str]]]]: The data for the specified trait.
        """
        return super()._load_uuid(uuid, "primary_traits.json")
