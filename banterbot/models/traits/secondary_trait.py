import numpy as np
from typing_extensions import Self

from banterbot.utils.traits.primary_trait import PrimaryTrait


class SecondaryTrait:
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
        primary_trait1: PrimaryTrait,
        primary_trait2: PrimaryTrait,
        cov: float = 0.95,
    ) -> Self:
        """
        Create a SecondaryTrait instance based on two primary traits, using a Gaussian distribution to select a value
        from a provided grid.

        Args:
            name (str): The name of the secondary trait.
            grid (list[list[str]]): A 5x5 nested list of strings representing potential trait values.
            primary_trait1 (PrimaryTrait): The first primary trait influencing the secondary trait.
            primary_trait2 (PrimaryTrait): The second primary trait influencing the secondary trait.
            cov (float): The covariance for the Gaussian distribution, defaulting to 0.95.

        Returns:
            SecondaryTrait: An instance of SecondaryTrait with selected value and description.

        Note:
            The grid is expected to be 5x5, and the `cov` parameter controls the spread of the Gaussian distribution.

            The values of the primary traits are treated as indices for the Gaussian distribution, thus no increment is
            needed.

            The final value is adjusted (+1) to match the 1-7 range of tertiary traits in the character trait generation
            system.
        """

        # Mean (mu) for the Gaussian distribution; primary_trait values become indices, so incrementing is unneeded.
        mu = [primary_trait1.value, primary_trait2.value]

        # Draw a sample from a multivariate normal distribution
        sample = np.random.multivariate_normal(mu, [[cov, 0], [0, cov]])

        # Round the sample to the nearest integer and clip to grid limits (0 to 4)
        sample_rounded = np.clip(np.round(sample).astype(int), 0, 4)

        # Get the corresponding value from the grid
        selected_value = grid[sample_rounded[0]][sample_rounded[1]]

        return cls(name, sample_rounded + 1, selected_value)

    def __str__(self) -> str:
        return f"{self.name}: {self.value} - {self.description}"


if __name__ == "__main__":

    def test_secondary_trait():
        primary_trait1 = PrimaryTrait("A", 2)
        primary_trait2 = PrimaryTrait("B", 3)

        # Sample grid (5x5)
        grid = [
            ["Trait1", "Trait2", "Trait3", "Trait4", "Trait5"],
            ["Trait6", "Trait7", "Trait8", "Trait9", "Trait10"],
            ["Trait11", "Trait12", "Trait13", "Trait14", "Trait15"],
            ["Trait16", "Trait17", "Trait18", "Trait19", "Trait20"],
            ["Trait21", "Trait22", "Trait23", "Trait24", "Trait25"],
        ]

        # Create a secondary trait using the class method
        secondary_trait = SecondaryTrait.from_primary_traits("TestTrait", grid, primary_trait1, primary_trait2)

        # Assertions to check if the secondary trait is within the expected range
        assert 1 <= secondary_trait.value[0] <= 5
        assert 1 <= secondary_trait.value[1] <= 5
        assert secondary_trait.description in [item for sublist in grid for item in sublist]

        print("Test Passed: SecondaryTrait created successfully with valid values and description.")

        print(secondary_trait)

    # Run the test
    test_secondary_trait()
