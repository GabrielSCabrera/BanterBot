import numpy as np
from typing_extensions import Self

from banterbot.models.traits.primary_trait import PrimaryTrait


class SecondaryTrait:
    """
    Secondary trait loading and management, with options for random generation, generation from primary traits, or
    specified parameters using data from instances of class `PrimaryTrait` or the `resources.secondary_traits` resource.
    """

    def __init__(self, uuid: str, name: str, description: str, value: int, value_description: str):
        """
        Initialize a SecondaryTrait instance.

        Args:
            uuid (str): The unique identifier of the secondary trait.
            name (str): The name of the secondary trait.
            description (str): A textual description of the secondary trait.
            value (int): The specific value of the secondary trait.
            value_description (str): Description of the trait at the specific value.
        """
        self.uuid = uuid
        self.name = name
        self.description = description
        self.value = value
        self.value_description = value_description

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
        # Mean (mu) for the Gaussian distribution.
        mu = [primary_trait_1.value + 1, primary_trait_2.value + 1]

        # Draw a sample from a multivariate normal distribution.
        sample = np.random.multivariate_normal(mu, [[cov, 0], [0, cov]])

        # Round the sample to the nearest integer and clip to grid limits (0 to 4).
        sample_rounded = np.clip(np.round(sample).astype(int), 0, 4)

        # Get the corresponding value from the grid.
        selected_value = grid[sample_rounded[0]][sample_rounded[1]]

        return cls(name, sample_rounded, selected_value)

    def __str__(self) -> str:
        return f"{self.name}: {self.value} - {self.description}"
