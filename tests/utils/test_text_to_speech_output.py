import datetime
import unittest

from banterbot.data.enums import SpeechProcessingType, WordCategory
from banterbot.managers.azure_neural_voice_manager import AzureNeuralVoiceManager
from banterbot.utils.speech_synthesis_output import SpeechSynthesisOutput
from banterbot.utils.word import Word


class TestSpeechSynthesisOutput(unittest.TestCase):
    """
    This test suite includes five test cases for the `SpeechSynthesisOutput` class:

        1. `test_text_to_speech_output_creation`: This test case checks if the `SpeechSynthesisOutput` instance is created
            with the correct attributes. It creates a `SpeechSynthesisOutput` instance with sample data and then asserts
            that each attribute has the expected value.

        2. `test_text_to_speech_output_getitem`: This test case checks if the `__getitem__` method of the
            `SpeechSynthesisOutput` class returns the correct word at the specified index. It creates a
            `SpeechSynthesisOutput` instance with sample data and then asserts that the word at the specified index is as
            expected.

        3. `test_text_to_speech_output_iter`: This test case checks if the `__iter__` method of the `SpeechSynthesisOutput`
            class provides an iterator to iterate over the words in the output. It creates a `SpeechSynthesisOutput`
            instance with sample data and then asserts that the words can be iterated over correctly.

        4. `test_text_to_speech_output_len`: This test case checks if the `__len__` method of the `SpeechSynthesisOutput`
            class returns the correct number of words in the output. It creates a `SpeechSynthesisOutput` instance with
            sample data and then asserts that the number of words in the output is as expected.

        5. `test_text_to_speech_output_str`: This test case checks if the `__str__` method of the `SpeechSynthesisOutput`
            class returns the correct string representation of the instance. It creates a `SpeechSynthesisOutput` instance
            with sample data and then asserts that the string representation of the instance is as expected.
    """

    def test_text_to_speech_output_creation(self):
        voice = AzureNeuralVoiceManager.load("Aria")
        style = voice.styles[0]
        tts_output = SpeechSynthesisOutput(
            input_string="Hello, world!",
            timestamp=datetime.datetime.now(),
            voice=voice,
            style=style,
        )

        self.assertEqual(tts_output.input_string, "Hello, world!")
        self.assertIsInstance(tts_output.timestamp, datetime.datetime)
        self.assertEqual(tts_output.voice.name, voice.name)
        self.assertEqual(tts_output.style, voice.styles[0])
        self.assertIsInstance(tts_output.words, list)

    def test_text_to_speech_output_getitem(self):
        voice = AzureNeuralVoiceManager.load("Aria")
        style = voice.styles[0]
        tts_output = SpeechSynthesisOutput(
            input_string="Hello, world!",
            timestamp=datetime.datetime.now(),
            voice=voice,
            style=style,
        )

        word1 = Word(
            word="Hello",
            offset=datetime.timedelta(seconds=0),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )
        word2 = Word(
            word=",",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.PUNCTUATION,
            source=SpeechProcessingType.TTS,
        )
        word3 = Word(
            word="world",
            offset=datetime.timedelta(seconds=2),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )

        tts_output.words.extend([word1, word2, word3])

        self.assertEqual(tts_output[0], word1)
        self.assertEqual(tts_output[1], word2)
        self.assertEqual(tts_output[2], word3)

    def test_text_to_speech_output_iter(self):
        voice = AzureNeuralVoiceManager.load("Aria")
        style = voice.styles[0]
        tts_output = SpeechSynthesisOutput(
            input_string="Hello, world!",
            timestamp=datetime.datetime.now(),
            voice=voice,
            style=style,
        )

        word1 = Word(
            word="Hello",
            offset=datetime.timedelta(seconds=0),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )
        word2 = Word(
            word=",",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.PUNCTUATION,
            source=SpeechProcessingType.TTS,
        )
        word3 = Word(
            word="world",
            offset=datetime.timedelta(seconds=2),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )

        tts_output.words.extend([word1, word2, word3])

        for idx, word in enumerate(tts_output):
            self.assertEqual(word, tts_output.words[idx])

    def test_text_to_speech_output_len(self):
        voice = AzureNeuralVoiceManager.load("Aria")
        style = voice.styles[0]
        tts_output = SpeechSynthesisOutput(
            input_string="Hello, world!",
            timestamp=datetime.datetime.now(),
            voice=voice,
            style=style,
        )

        word1 = Word(
            word="Hello",
            offset=datetime.timedelta(seconds=0),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )
        word2 = Word(
            word=",",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.PUNCTUATION,
            source=SpeechProcessingType.TTS,
        )
        word3 = Word(
            word="world",
            offset=datetime.timedelta(seconds=2),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )

        tts_output.words.extend([word1, word2, word3])

        self.assertEqual(len(tts_output), 3)

    def test_text_to_speech_output_str(self):
        voice = AzureNeuralVoiceManager.load("Aria")
        style = voice.styles[0]
        tts_output = SpeechSynthesisOutput(
            input_string="Hello, world!",
            timestamp=datetime.datetime.now(),
            voice=voice,
            style=style,
        )

        word1 = Word(
            word="Hello",
            offset=datetime.timedelta(seconds=0),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )
        word2 = Word(
            word=",",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.PUNCTUATION,
            source=SpeechProcessingType.TTS,
        )
        word3 = Word(
            word="world",
            offset=datetime.timedelta(seconds=2),
            duration=datetime.timedelta(seconds=1),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
        )

        tts_output.words.extend([word1, word2, word3])

        self.assertEqual(str(tts_output), "Hello,world")


if __name__ == "__main__":
    unittest.main()
