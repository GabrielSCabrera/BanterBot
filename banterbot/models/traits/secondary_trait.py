import numpy as np
from typing_extensions import Self

from banterbot.models.traits.primary_trait import PrimaryTrait
from banterbot.models.traits.trait import Trait


class SecondaryTrait(Trait):
    """
    Secondary trait loading and management, with options for random generation, generation from primary traits, or
    specified parameters using data from instances of class `PrimaryTrait` or the `resources.secondary_traits` resource.
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

        # Mean (mu) for the Gaussian distribution.
        mu = [primary_trait_1.value + 1, primary_trait_2.value + 1]

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
    def _load_uuid(cls, uuid: str):
        """
        Helper method to load trait data from the `secondary_traits` JSON based on UUID.

        Args:
            uuid (str): The UUID of the trait.

        Returns:
            dict: The data for the specified trait.
        """
        return super()._load_uuid(uuid=uuid, resource="secondary_traits.json")
