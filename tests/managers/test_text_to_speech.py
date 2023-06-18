import datetime
import time
import unittest
from unittest.mock import patch

from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat

from banterbot.data.azure_neural_voices import AzureNeuralVoice, get_voice_by_name
from banterbot.data.enums import SpeechProcessingType, WordCategory
from banterbot.managers.text_to_speech import TextToSpeech
from banterbot.utils.text_to_speech_output import TextToSpeechOutput
from banterbot.utils.word import Word


class TestTextToSpeech(unittest.TestCase):
    """
    This test suite covers the main functionality of the `TextToSpeech` class. The `setUp` method initializes an
    instance of `TextToSpeech` with mocked methods to avoid making actual API calls. The tests cover the following
    scenarios:

        1. Test the initialization of the `TextToSpeech` class.
        2. Test the `interrupt` method.
        3. Test the `speak` method, including the processing of words and updating the output object.

    Please note that these tests do not require API keys and do not make actual API calls, as the relevant methods are
    mocked using the `unittest.mock.patch` decorator.
    """

    def setUp(self) -> None:
        self.voice = get_voice_by_name("Aria")
        self.style = "cheerful"
        self.input_string = "Hello, world!"
        self.output_format = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3

        # Mock the TextToSpeech class to avoid making actual API calls
        method_1 = "banterbot.managers.text_to_speech.TextToSpeech._callbacks_connect"
        method_2 = "banterbot.managers.text_to_speech.TextToSpeech._speak"
        with patch(method_1), patch(method_2):
            self.tts = TextToSpeech(output_format=self.output_format)

    def test_init(self) -> None:
        self.assertIsNotNone(self.tts)
        self.assertEqual(self.tts.output, [])

    def test_interrupt(self) -> None:
        t0 = time.perf_counter_ns()
        self.tts.interrupt()
        self.assertGreater(self.tts._interrupt, t0)

    def test_speak(self) -> None:
        with patch.object(self.tts, "_callbacks_process") as mock_process, patch.object(self.tts, "_speak"):
            words = ["Hello", ",", " world", "!"]
            offset_seconds = [0, 1, 1.5, 2.5]
            duration_seconds = [1, 0.5, 1, 0.5]
            categories = [WordCategory.WORD, WordCategory.PUNCTUATION, WordCategory.WORD, WordCategory.PUNCTUATION]
            source = SpeechProcessingType.TTS
            words = [
                Word(
                    word=word,
                    offset=datetime.timedelta(seconds=offset),
                    duration=datetime.timedelta(seconds=duration),
                    category=category,
                    source=source,
                )
                for word, offset, duration, category in zip(words, offset_seconds, duration_seconds, categories)
            ]
            mock_process.return_value = iter(words)

            words = list(self.tts.speak(self.input_string, self.voice, self.style))

            self.assertEqual(len(words), 4)
            self.assertEqual(words[0].word, "Hello")
            self.assertEqual(words[1].word, ",")
            self.assertEqual(words[2].word, " world")
            self.assertEqual(words[3].word, "!")

            output = self.tts.output[-1]
            self.assertIsInstance(output, TextToSpeechOutput)
            self.assertEqual(output.input_string, self.input_string)
            self.assertEqual(output.voice, self.voice)
            self.assertEqual(output.style, self.style)

            # Update the output object with the processed words
            for word in words:
                output.append(word)

            self.assertEqual(len(output.words), 4)


if __name__ == "__main__":
    unittest.main()
