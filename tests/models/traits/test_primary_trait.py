import unittest
from unittest.mock import patch

from banterbot.models.traits.primary_trait import PrimaryTrait


class TestPrimaryTrait(unittest.TestCase):
    def test_load_random(self):
        uuid = "018cb673-53c9-8e71-b7ae-0b99dd0cf9d4"
        name = "Openness"
        description = "Creativity, curiosity, openness to new experiences"
        value = 2
        value_description = "Inventive"

        with patch("random.randrange", return_value=value):
            primary_trait = PrimaryTrait.load_random(uuid)

        self.assertEqual(primary_trait.name, name)
        self.assertEqual(primary_trait.description, description)
        self.assertEqual(primary_trait.value, value)
        self.assertEqual(primary_trait.value_description, value_description)

    def test_load_select(self):
        uuid = "018cb673-53c9-8e71-b7ae-0b99dd0cf9d4"
        name = "Openness"
        description = "Creativity, curiosity, openness to new experiences"
        value = 2
        value_description = "Inventive"

        primary_trait = PrimaryTrait.load_select(uuid, value)

        self.assertEqual(primary_trait.name, name)
        self.assertEqual(primary_trait.description, description)
        self.assertEqual(primary_trait.value, value)
        self.assertEqual(primary_trait.value_description, value_description)

    def test_load_select_invalid_value(self):
        uuid = "018cb673-53c9-8e71-b7ae-0b99dd0cf9d4"
        value = 4

        data = {
            "name": "Openness",
            "description": "Creativity, curiosity, openness to new experiences",
            "levels": ["Cautious", "Balanced", "Inventive"],
        }

        with self.assertRaises(IndexError):
            PrimaryTrait.load_select(uuid, value)


if __name__ == "__main__":
    unittest.main()
