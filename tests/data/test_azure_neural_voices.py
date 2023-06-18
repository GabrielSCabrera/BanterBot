import unittest

from banterbot.data.azure_neural_voices import (
    AzureNeuralVoice,
    AzureNeuralVoiceGender,
    get_voice_by_name,
    get_voices_by_gender,
)


class TestAzureNeuralVoices(unittest.TestCase):
    """
    This test suite includes tests for the `get_voice_by_name` and `get_voices_by_gender` functions. The tests check for
    valid and invalid voice names, case-insensitivity, and proper filtering of voices by gender.
    """

    def test_get_voice_by_name(self):
        # Test valid voice name
        voice = get_voice_by_name("Aria")
        self.assertIsInstance(voice, AzureNeuralVoice)
        self.assertEqual(voice.name, "Aria")

        # Test case-insensitivity
        voice = get_voice_by_name("aria")
        self.assertIsInstance(voice, AzureNeuralVoice)
        self.assertEqual(voice.name, "Aria")

        # Test invalid voice name
        with self.assertRaises(KeyError):
            get_voice_by_name("InvalidVoice")

    def test_get_voices_by_gender(self):
        # Test male voices
        male_voices = get_voices_by_gender(AzureNeuralVoiceGender.MALE)
        self.assertTrue(all(voice.gender == AzureNeuralVoiceGender.MALE for voice in male_voices))

        # Test female voices
        female_voices = get_voices_by_gender(AzureNeuralVoiceGender.FEMALE)
        self.assertTrue(all(voice.gender == AzureNeuralVoiceGender.FEMALE for voice in female_voices))


if __name__ == "__main__":
    unittest.main()
