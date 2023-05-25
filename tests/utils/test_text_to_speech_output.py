"""
These tests cover various aspects of the TextToSpeechOutput class, including retrieving words by index, iterating over
words, getting the length of the output, setting values at a specific index, converting the output to a string,
appending new words, stopping the output process, and streaming words from the output.
"""
import datetime
import unittest
from typing import List

import azure.cognitiveservices.speech as speechsdk

from banterbot.utils.text_to_speech_output import TextToSpeechOutput
from banterbot.utils.text_to_speech_word import TextToSpeechWord


class TextToSpeechOutputTestCase(unittest.TestCase):
    def setUp(self):
        self.output = TextToSpeechOutput("Hello, world!")

        timestamp = datetime.datetime.now()
        dt = datetime.timedelta(seconds=1)

        word1 = TextToSpeechWord(
            word="Hello", timestamp=timestamp, word_index=0, category=speechsdk.SpeechSynthesisBoundaryType.Word
        )
        word2 = TextToSpeechWord(
            word=",", timestamp=timestamp + dt, word_index=1, category=speechsdk.SpeechSynthesisBoundaryType.Punctuation
        )
        word3 = TextToSpeechWord(
            word=" world",
            timestamp=timestamp + 2 * dt,
            word_index=2,
            category=speechsdk.SpeechSynthesisBoundaryType.Word,
        )
        word4 = TextToSpeechWord(
            word="!",
            timestamp=timestamp + 3 * dt,
            word_index=3,
            category=speechsdk.SpeechSynthesisBoundaryType.Punctuation,
        )

        words = [word1, word2, word3, word4]
        for word in words:
            self.output.append(word)

    def test_getitem(self):
        word = self.output[0]
        self.assertIsInstance(word, TextToSpeechWord)
        self.assertEqual(word.word, "Hello")

    def test_iter(self):
        words = list(self.output)
        self.assertIsInstance(words, List)
        self.assertEqual(len(words), len(self.output))
        self.assertIsInstance(words[0], TextToSpeechWord)
        self.assertEqual(words[0].word, "Hello")

    def test_len(self):
        length = len(self.output)
        self.assertEqual(length, 4)

    def test_setitem(self):
        word = TextToSpeechWord(
            word="Earth",
            timestamp=datetime.datetime.now(),
            word_index=2,
            category=speechsdk.SpeechSynthesisBoundaryType.Word,
        )
        self.output[2] = word
        self.assertEqual(self.output[2].word, "Earth")

    def test_str(self):
        string = str(self.output)
        self.assertEqual(string, "Hello, world!")

    def test_append(self):
        word = TextToSpeechWord(
            word=" Yup",
            timestamp=datetime.datetime.now(),
            word_index=4,
            category=speechsdk.SpeechSynthesisBoundaryType.Word,
        )
        self.output.append(word)
        self.assertEqual(len(self.output), 5)
        self.assertEqual(self.output[4].word, " Yup")


if __name__ == "__main__":
    unittest.main()
