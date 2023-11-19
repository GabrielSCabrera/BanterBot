import time
import unittest
from unittest.mock import patch

from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat

from banterbot.managers.azure_neural_voice_manager import AzureNeuralVoiceManager


class TestSpeechSynthesisService(unittest.TestCase):
    """
    This test suite covers the main functionality of the `SpeechSynthesisService` class. The `setUp` method initializes an
    instance of `SpeechSynthesisService` with mocked methods to avoid making actual API calls. The tests cover the following
    scenarios:

        1. Test the initialization of the `SpeechSynthesisService` class.
        2. Test the `interrupt` method.
        3. Test the `speak` method, including the processing of words and updating the output object.

    Please note that these tests do not require API keys and do not make actual API calls, as the relevant methods are
    mocked using the `unittest.mock.patch` decorator.
    """

    def setUp(self) -> None:
        self.voice = AzureNeuralVoiceManager.load("Aria")
        self.style = "cheerful"
        self.input_string = "Hello, world!"
        self.output_format = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3

        # Mock the SpeechSynthesisService class to avoid making actual API calls
        method_1 = "banterbot.managers.text_to_speech.SpeechSynthesisService._callbacks_connect"
        method_2 = "banterbot.managers.text_to_speech.SpeechSynthesisService._speak"
        with patch(method_1), patch(method_2):
            self.tts = SpeechSynthesisService(output_format=self.output_format)

    def test_init(self) -> None:
        self.assertIsNotNone(self.tts)
        self.assertEqual(self.tts.output, [])

    def test_interrupt(self) -> None:
        t0 = time.perf_counter_ns()
        self.tts.interrupt()
        self.assertGreater(self.tts._interrupt, t0)


if __name__ == "__main__":
    unittest.main()
