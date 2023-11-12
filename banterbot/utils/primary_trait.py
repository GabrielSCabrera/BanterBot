import json
import random
from typing import Optional
import importlib.resources
import banterbot.resources


class PrimaryTrait:

    traits_data = None

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
    def load_random(cls, uuid: str):
        """
        Load a PrimaryTrait instance based on a UUID with a randomly selected value.

        Args:
            uuid (str): The unique identifier of the primary trait.

        Returns:
            PrimaryTrait: An instance of PrimaryTrait with a randomly selected value.
        """
        if data is None:
            data = cls._load_uuid(uuid)

        value = random.randrange(len(data["levels"]))

        value_description = data["levels"][value]
        return cls(data["name"], data["description"], value, value_description)

    @classmethod
    def load_select(cls, uuid: str, value: int):
        """
        Load a PrimaryTrait instance based on a UUID with a specified value.

        Args:
            uuid (str): The unique identifier of the primary trait.
            value (int): The specified value for the trait.

        Returns:
            PrimaryTrait: An instance of PrimaryTrait with the specified value.
        """
        if data is None:
            data = cls._load_uuid(uuid)

        if not isinstance(value, int) or 0 > value >= len(data["levels"]):
            raise ValueError("Specified value is out of the valid range for this trait.")

        value_description = data["levels"][value - data["range"][0]]
        return cls(data["name"], data["description"], value, value_description)

    @classmethod
    def _load_uuid(cls, uuid: str):
        """
        Helper method to load trait data from JSON based on UUID. Only loads data once to reduce overhead, and saves
        the JSON dict to cache in class attribute `traits_data`.

        Args:
            uuid (str): The UUID of the trait.

        Returns:
            dict: The data of the trait.
        """
        if cls.traits_data is None:
            # Load the JSON data if it is not already cached.
            with open(importlib.resources.files(banterbot.resources).joinpath("traits.json"), "r") as fs:
                cls.traits_data = json.load(fs)

        # Search for the trait data based on UUID
        for traits in cls.traits_data["primary_traits"].values():
            if uuid in traits:
                return traits[uuid]
