import datetime
import json
import unittest
from unittest.mock import MagicMock

from banterbot.utils.speech_to_text_output import SpeechRecognitionOutput


class TestSpeechToTextOutput(unittest.TestCase):
    """
    This test suite includes test cases for the `SpeechToTextOutput` class:

        1.  `test_recognition_status`: This test case checks if the `recognition_status` property returns the correct
             recognition status from the speech recognition result.

        2.  `test_offset`: This test case checks if the `offset` property returns the correct offset of the recognized
             speech in the audio stream.

        3.  `test_duration`: This test case checks if the `duration` property returns the correct duration of the
             recognized speech in the audio stream.

        4.  `test_confidence`: This test case checks if the `confidence` property returns the correct confidence score
             of the recognized speech.

        5.  `test_lexical`: This test case checks if the `lexical` property returns the correct lexical form of the
             recognized speech.

        6.  `test_ITN`: This test case checks if the `ITN` property returns the correct ITN (Inverse Text Normalization)
             form of the recognized speech.

        7.  `test_maskedITN`: This test case checks if the `maskedITN` property returns the correct masked ITN (Inverse
             Text Normalization) form of the recognized speech.

        8.  `test_display`: This test case checks if the `display` property returns the correct display form of the
             recognized speech, which is fully processed with Inverse Text Normalization (ITN), Capitalization,
             Disfluency Removal, and Punctuation.

        9.  `test_words`: This test case checks if the `words` property returns the correct list of Word objects
             extracted from the speech recognition result.

        10. `test_sents`: This test case checks if the `sents` property returns the correct list of sentences extracted
             from the speech recognition result.

        11. `test_getitem`: This test case checks if the `__getitem__` method allows for indexing into the
             SpeechToTextOutput object to retrieve words at specific positions.

        12. `test_iter`: This test case checks if the `__iter__` method allows for iteration over the Word objects in
             the output.

        13. `test_len`: This test case checks if the `__len__` method allows for the use of len() on a
             SpeechToTextOutput instance, returning the number of words in the output.

        14. `test_str`: This test case checks if the `__str__` method allows for the use of str() on a
             SpeechToTextOutput instance, returning the fully processed speech-to-text output.

    The purpose of this test suite is to ensure that the SpeechToTextOutput class correctly processes and stores the
    speech recognition result data, and provides the expected functionality for accessing and manipulating the data.
    """

    def setUp(self):
        json_data = json.dumps(
            {
                "RecognitionStatus": "Success",
                "Offset": 1000000,
                "Duration": 2000000,
                "NBest": [
                    {
                        "Confidence": 0.9,
                        "Lexical": "hello world",
                        "ITN": "hello world",
                        "MaskedITN": "hello world",
                        "Display": "Hello, world.",
                        "Words": [
                            {"Word": "Hello", "Offset": 1000000, "Duration": 1000000, "Confidence": 0.9},
                            {"Word": ",", "Offset": 2000000, "Duration": 100000, "Confidence": 0.9},
                            {"Word": "world", "Offset": 2100000, "Duration": 900000, "Confidence": 0.9},
                            {"Word": ".", "Offset": 3000000, "Duration": 100000, "Confidence": 0.9},
                        ],
                    }
                ],
            }
        )
        self.recognition_result = MagicMock()
        self.recognition_result.json = json_data
        self.stt_output = SpeechRecognitionOutput(recognition_result=self.recognition_result)

    def test_recognition_status(self):
        self.assertEqual(self.stt_output.recognition_status, "Success")

    def test_offset(self):
        self.assertEqual(self.stt_output.offset, datetime.timedelta(seconds=0.1))

    def test_duration(self):
        self.assertEqual(self.stt_output.duration, datetime.timedelta(seconds=0.2))

    def test_confidence(self):
        self.assertEqual(self.stt_output.confidence, 0.9)

    def test_lexical(self):
        self.assertEqual(self.stt_output.lexical, "hello world")

    def test_ITN(self):
        self.assertEqual(self.stt_output.ITN, "hello world")

    def test_maskedITN(self):
        self.assertEqual(self.stt_output.maskedITN, "hello world")

    def test_display(self):
        self.assertEqual(self.stt_output.display, "Hello, world.")

    def test_words(self):
        self.assertEqual(len(self.stt_output.words), 4)
        self.assertEqual(self.stt_output.words[0].word, "Hello")
        self.assertEqual(self.stt_output.words[1].word, ",")
        self.assertEqual(self.stt_output.words[2].word, "world")
        self.assertEqual(self.stt_output.words[3].word, ".")

    def test_sents(self):
        self.assertEqual(len(self.stt_output.sents), 1)
        self.assertEqual(self.stt_output.sents[0], "Hello, world.")

    def test_getitem(self):
        self.assertEqual(self.stt_output[0].word, "Hello")
        self.assertEqual(self.stt_output[1].word, ",")
        self.assertEqual(self.stt_output[2].word, "world")
        self.assertEqual(self.stt_output[3].word, ".")

    def test_iter(self):
        words = [word for word in self.stt_output]
        self.assertEqual(len(words), 4)
        self.assertEqual(words[0].word, "Hello")
        self.assertEqual(words[1].word, ",")
        self.assertEqual(words[2].word, "world")
        self.assertEqual(words[3].word, ".")

    def test_len(self):
        self.assertEqual(len(self.stt_output), 4)

    def test_str(self):
        self.assertEqual(str(self.stt_output), "Hello, world.")


if __name__ == "__main__":
    unittest.main()
