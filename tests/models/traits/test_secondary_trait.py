import unittest
from unittest.mock import patch

import numpy as np

from banterbot.models.traits.primary_trait import PrimaryTrait
from banterbot.models.traits.secondary_trait import SecondaryTrait


class TestSecondaryTrait(unittest.TestCase):
    def test_from_primary_traits(self):
        uuid = "018cb674-43d2-811e-ae36-78e2b25912fb"
        name = "Adaptability"
        description = "Reflects how easily a character adapts to hierarchical structures and new ideas"
        value = np.array([3, 2])
        value_description = "Dynamic"

        primary_trait_1 = PrimaryTrait.load_select(uuid="018cb673-53c9-8e71-b7ae-0b99dd0cf9d4", value=2)
        primary_trait_2 = PrimaryTrait.load_select(uuid="018cb673-53ca-8673-a19f-788d87a8d1fb", value=1)

        with patch("numpy.random.multivariate_normal", return_value=value):
            secondary_trait = SecondaryTrait.from_primary_traits(uuid, primary_trait_1, primary_trait_2)

        self.assertEqual(secondary_trait.uuid, uuid)
        self.assertEqual(secondary_trait.name, name)
        self.assertEqual(secondary_trait.description, description)
        np.testing.assert_array_equal(secondary_trait.value, value)
        self.assertEqual(secondary_trait.value_description, value_description)

    def test__load_uuid(self):
        uuid = "018cb674-43d2-811e-ae36-78e2b25912fb"

        data = {
            "name": "Adaptability",
            "description": "Reflects how easily a character adapts to hierarchical structures and new ideas",
            "derived_from": ["018cb673-53c9-8e71-b7ae-0b99dd0cf9d4", "018cb673-53ca-8673-a19f-788d87a8d1fb"],
            "levels": [
                ["Resistant", "Slightly Adaptable", "Moderate", "Adaptable", "Highly Adaptable"],
                ["Traditional", "Conventional", "Flexible", "Open-Minded", "Innovative"],
                ["Stubborn", "Hesitant", "Versatile", "Eager", "Pioneering"],
                ["Rigid", "Cautious", "Dynamic", "Creative", "Visionary"],
                ["Conservative", "Slow to Change", "Resourceful", "Progressive", "Revolutionary"],
            ],
        }

        with patch(
            "banterbot.models.traits.secondary_trait.Trait._load_uuid",
            return_value=data,
        ) as mock_load_uuid:
            result = SecondaryTrait._load_uuid(uuid)

        mock_load_uuid.assert_called_once_with(uuid=uuid, resource="secondary_traits.json")
        self.assertEqual(result, data)


if __name__ == "__main__":
    unittest.main()
