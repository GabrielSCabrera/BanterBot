"""
These tests cover getting the length of the word, converting the word to a string representation, and getting the word
as a string representation.
"""
import datetime
import unittest
from dataclasses import dataclass

import azure.cognitiveservices.speech as speechsdk

from banterbot.utils.text_to_speech_word import TextToSpeechWord


@dataclass(frozen=True)
class MockSpeechSynthesisBoundaryType:
    WORD = "word"
    PUNCTUATION = "punctuation"


class TextToSpeechWordTestCase(unittest.TestCase):
    def setUp(self):
        self.timestamp = datetime.datetime.now()
        self.word = TextToSpeechWord(
            word="Hello", timestamp=self.timestamp, word_index=0, category=speechsdk.SpeechSynthesisBoundaryType.Word
        )

    def test_len(self):
        length = len(self.word)
        self.assertEqual(length, 5)

    def test_str(self):
        string = str(self.word)
        expected_string = f"<TextToSpeechWord 'Hello' at {self.timestamp.isoformat()}>"
        self.assertEqual(string, expected_string)

    def test_repr(self):
        representation = repr(self.word)
        self.assertEqual(representation, "Hello")


if __name__ == "__main__":
    unittest.main()
