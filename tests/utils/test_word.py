import datetime
import unittest

from banterbot.data.enums import SpeechProcessingType, WordCategory
from banterbot.utils.word import Word


class TestWord(unittest.TestCase):
    """
    This test suite includes four test cases for the `Word` class:

        1. `test_word_creation`: This test case checks if the `Word` instance is created with the correct attributes. It
            creates a `Word` instance with sample data and then asserts that each attribute has the expected value.

        2. `test_word_len`: This test case checks if the `__len__` method of the `Word` class returns the correct length
            of the word. It creates a `Word` instance with sample data and then asserts that the length of the word is
            as expected.

        3. `test_word_str`: This test case checks if the `__str__` method of the `Word` class returns the correct string
            representation of the instance. It creates a `Word` instance with sample data and then asserts that the
            string representation of the instance is as expected.

        4. `test_word_repr`: This test case checks if the `__repr__` method of the `Word` class returns the correct
            string representation of the word itself. It creates a `Word` instance with sample data and then asserts
            that the string representation of the word is as expected.
    """

    def test_word_creation(self):
        word = Word(
            word="hello",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=2),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
            confidence=0.9,
        )

        self.assertEqual(word.word, "hello")
        self.assertEqual(word.offset, datetime.timedelta(seconds=1))
        self.assertEqual(word.duration, datetime.timedelta(seconds=2))
        self.assertEqual(word.category, WordCategory.WORD)
        self.assertEqual(word.source, SpeechProcessingType.TTS)
        self.assertEqual(word.confidence, 0.9)

    def test_word_len(self):
        word = Word(
            word="hello",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=2),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
            confidence=0.9,
        )

        self.assertEqual(len(word), 5)

    def test_word_str(self):
        word = Word(
            word="hello",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=2),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
            confidence=0.9,
        )

        expected_str = "<word: `hello` | offset: 1s | duration: 2s | source: TTS>"
        self.assertEqual(str(word), expected_str)

    def test_word_repr(self):
        word = Word(
            word="hello",
            offset=datetime.timedelta(seconds=1),
            duration=datetime.timedelta(seconds=2),
            category=WordCategory.WORD,
            source=SpeechProcessingType.TTS,
            confidence=0.9,
        )

        self.assertEqual(repr(word), "hello")


if __name__ == "__main__":
    unittest.main()
