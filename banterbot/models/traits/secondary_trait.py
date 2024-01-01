from typing import Union

import numpy as np
from typing_extensions import Self

from banterbot.models.traits.primary_trait import PrimaryTrait
from banterbot.models.traits.trait import Trait


class SecondaryTrait(Trait):
    """
    Secondary trait loading and management, with options for random generation, generation from primary traits, or
    specified parameters using data from instances of class `PrimaryTrait` or the `resources.secondary_traits` resource.

    Attributes:
        uuid (str): The unique identifier for the trait.
        name (str): The name of the trait.
        description (str): The description of the trait.
        value (np.ndarray): The value of the trait.
        value_description (str): The description of the trait value.
    """

    @classmethod
    def from_primary_traits(
        cls,
        uuid: str,
        primary_trait_1: PrimaryTrait,
        primary_trait_2: PrimaryTrait,
        cov: float = 0.95,
    ) -> Self:
        """
        Create a SecondaryTrait instance based on two primary traits, using a 2-D multivariate Gaussian distribution to
        select a value from the provided grid.

        Args:
            uuid (str): The unique identifier of the secondary trait.
            primary_trait_1 (PrimaryTrait): The first primary trait influencing the secondary trait.
            primary_trait_2 (PrimaryTrait): The second primary trait influencing the secondary trait.
            cov (float): The covariance for the Gaussian distribution, defaults to 0.95.

        Returns:
            SecondaryTrait: An instance of SecondaryTrait with selected value and description.
        """
        data = cls._load_uuid(uuid)
        primary_traits = cls._sort_traits(data=data, primary_trait_1=primary_trait_1, primary_trait_2=primary_trait_2)

        # Mean (mu) for the Gaussian distribution.
        mu = [primary_trait.value + 1 for primary_trait in primary_traits]

        # Draw a sample from a multivariate normal distribution.
        sample = np.random.multivariate_normal(mu, [[cov, 0], [0, cov]])

        # Round the sample to the nearest integer and clip to grid limits (0 to 4).
        value = np.clip(np.round(sample).astype(int), 0, 4)

        # Get the corresponding value from the grid.
        value_description = data["levels"][value[0]][value[1]]

        return cls(
            uuid=uuid,
            name=data["name"],
            description=data["description"],
            value=value,
            value_description=value_description,
        )

    @classmethod
    def _sort_traits(
        cls,
        data: dict[str, dict[str, Union[str, list[str], list[list[str]]]]],
        primary_trait_1: PrimaryTrait,
        primary_trait_2: PrimaryTrait,
    ) -> list[PrimaryTrait]:
        """
        Helper method to sort primary traits based on the order they are specified in the `derived_from` list. This
        ensures that the correct primary traits are used to generate the secondary trait, and sorts them in the correct
        order for the multivariate Gaussian distribution.

        Args:
            data (dict): The data for the secondary trait.
            primary_trait_1 (PrimaryTrait): The first primary trait influencing the secondary trait.
            primary_trait_2 (PrimaryTrait): The second primary trait influencing the secondary trait.

        Returns:
            list: The sorted list of primary traits.
        """

        if primary_trait_1.uuid == primary_trait_2.uuid:
            raise ValueError(
                f"Primary trait `{primary_trait_1.uuid}` cannot be used twice for secondary trait `{data['uuid']}`."
            )
        elif primary_trait_1.uuid not in data["derived_from"]:
            raise ValueError(
                f"Primary trait `{primary_trait_1.uuid}` is not a valid primary trait for secondary trait"
                f" `{data['uuid']}`."
            )
        elif primary_trait_2.uuid not in data["derived_from"]:
            raise ValueError(
                f"Primary trait `{primary_trait_2.uuid}` is not a valid primary trait for secondary trait"
                f" `{data['uuid']}`."
            )
        else:
            traits = [primary_trait_1, primary_trait_2]
            return sorted(traits, key=lambda trait: data["derived_from"].index(trait.uuid))

    @classmethod
    def _load_uuid(cls, uuid: str) -> dict[str, dict[str, Union[str, list[str], list[list[str]]]]]:
        """
        Helper method to load trait data from the `secondary_traits` JSON based on UUID.

        Args:
            uuid (str): The UUID of the secondary trait.

        Returns:
            dict[str, dict[str, Union[str, list[str], list[list[str]]]]]: The data for the specified trait.
        """
        return super()._load_uuid(uuid=uuid, resource="secondary_traits.json")
