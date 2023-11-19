import threading
import time
import unittest
from unittest.mock import MagicMock, patch

import azure.cognitiveservices.speech as speechsdk

from banterbot.services.speech_synthesis_service import SpeechToText


class TestSpeechToText(unittest.TestCase):
    """
    This test suite covers the main functionality of the `SpeechToText` class. The `setUp` method initializes an
    instance of `SpeechToText` with mocked methods to avoid making actual API calls. The tests cover the following
    scenarios:

        1. Test the `interrupt` method to ensure that it updates the interrupt flag.
        2. Test the `listen` method to ensure that it processes recognized speech events and appends them to the output
           list.
        3. Test the `listening` property to ensure that it returns the correct listening state.

    Note that these tests do not make actual API calls and do not require API keys. They use the `unittest` package
    and can be run for free.
    """

    def setUp(self):
        # Mock the Azure Cognitive Services speech configuration and recognizer
        with patch("azure.cognitiveservices.speech.SpeechConfig") as mock_speech_config, patch(
            "azure.cognitiveservices.speech.SpeechRecognizer"
        ) as mock_speech_recognizer, patch("azure.cognitiveservices.speech.Connection") as mock_connection:
            # Create a SpeechToText instance with the mocked configuration and recognizer
            self.speech_to_text = SpeechToText()

            # Set the mocked configuration, recognizer, and connection as attributes of the SpeechToText instance
            self.speech_to_text._speech_config = mock_speech_config
            self.speech_to_text._recognizer = mock_speech_recognizer
            self.speech_to_text._connection = mock_connection
        self.text = ""

    def test_interrupt(self):
        # Test the interrupt method
        self.speech_to_text.interrupt()
        self.assertGreater(self.speech_to_text._interrupt, 0)

    def test_listen(self):
        # Mock the speech recognition result
        mock_result = MagicMock()
        mock_result.text = "Hello, world!"
        mock_result.reason = speechsdk.ResultReason.RecognizedSpeech

        # Mock the recognized event
        mock_event = MagicMock()
        mock_event.result = mock_result

        # Set the mocked recognized event as the return value of the wait_for_next_event method
        self.speech_to_text._recognizer.recognized.connect.side_effect = lambda callback: callback(mock_event)

        def thread():
            for block in self.speech_to_text.listen():
                self.text += block

        # Test the listen method
        with patch.object(self.speech_to_text, "_callbacks_process", return_value=["Hello, world!"]):
            thread = threading.Thread(target=thread, daemon=True)
            thread.start()

            t0 = time.perf_counter_ns()
            dt = 0
            timeout = 1e8
            while self.text != "Hello, world!" and dt < timeout:
                dt = time.perf_counter_ns() - t0

            self.speech_to_text.interrupt()

            self.assertEqual(self.text, "Hello, world!")

    def test_listening(self):
        # Test the listening property
        self.speech_to_text._listening = True
        self.assertTrue(self.speech_to_text.listening)

        self.speech_to_text._listening = False
        self.assertFalse(self.speech_to_text.listening)


if __name__ == "__main__":
    unittest.main()
