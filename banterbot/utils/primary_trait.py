class PrimaryTrait:
    def __init__(self, name, value):
        self.name = name  # The name of the trait (e.g., "Openness", "Collectivism")
        self.value = value  # Value of the trait, ranging from 1 to 3

    def __str__(self):
        return f"{self.name}: {self.value}"
