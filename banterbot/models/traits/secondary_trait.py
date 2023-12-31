import numpy as np
from typing_extensions import Self

from banterbot.models.traits.primary_trait import PrimaryTrait


class SecondaryTrait:
    """
    Secondary trait loading and management, with options for random generation, generation from primary traits, or
    specified parameters using data from instances of class `PrimaryTrait` or the `resources.secondary_traits` resource.
    """

    def __init__(self, name: str, value: np.ndarray, description: str) -> None:
        """
        Initialize a SecondaryTrait instance.

        Args:
            name (str): The name of the secondary trait.
            value (np.ndarray): The numerical value of the secondary trait.
            description (str): A textual description of the secondary trait.
        """
        self.name = name
        self.value = value
        self.description = description

    @classmethod
    def from_primary_traits(
        cls,
        name: str,
        grid: list[list[str]],
        primary_trait_1: PrimaryTrait,
        primary_trait_2: PrimaryTrait,
        cov: float = 0.95,
    ) -> Self:
        """
        Create a SecondaryTrait instance based on two primary traits, using a 2-D multivariate Gaussian distribution to
        select a value from the provided grid.

        Args:
            name (str): The name of the secondary trait.
            grid (list[list[str]]): A 5x5 nested list of strings representing potential trait values.
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
