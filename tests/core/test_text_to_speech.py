import unittest
from unittest.mock import MagicMock, patch

from azure.cognitiveservices.speech import SpeechSynthesisBoundaryType, SpeechSynthesisOutputFormat, SpeechSynthesizer
from banterbot.core.text_to_speech import TextToSpeech
from banterbot.utils.text_to_speech_output import TextToSpeechOutput


class TestTextToSpeech(unittest.TestCase):
    def setUp(self):
        self.tts = TextToSpeech()
        self.tts._synthesizer = MagicMock(spec=SpeechSynthesizer)
        self.tts._speech_config = MagicMock()
        self.tts._outputs = []
        self.tts._boundaries = []
        self.tts._interrupt = False
        self.tts._synthesis_completed = False
        self.tts._start_synthesis = MagicMock()
        self.tts._connection = MagicMock()

    def test_init(self):
        self.assertIsNotNone(self.tts._speech_config)
        self.assertIsNotNone(self.tts._synthesizer)
        self.assertIsNotNone(self.tts._connection)

    def test_interrupt(self):
        self.tts.interrupt()
        self.assertTrue(self.tts._interrupt)

    def test_create_ssml(self):
        ssml = self.tts._create_ssml("Hello World", "en-US", "happy")
        self.assertIn('<voice name="en-US">', ssml)
        self.assertIn('<mstts:express-as style="happy">Hello World</mstts:express-as>', ssml)

    def test_reset(self):
        self.tts._reset()
        self.assertEqual(self.tts._boundaries, [])
        self.assertFalse(self.tts._interrupt)
        self.assertFalse(self.tts._synthesis_completed)
        self.assertFalse(self.tts._start_synthesis.is_set())

    def test_callback_completed(self):
        event = MagicMock()
        self.tts._callback_completed(event)
        self.assertTrue(self.tts._synthesis_completed)

    def test_callback_started(self):
        event = MagicMock()
        self.tts._callback_started(event)
        self.assertTrue(self.tts._start_synthesis.is_set())

    def test_callback_word_boundary(self):
        event = MagicMock()
        event.boundary_type = SpeechSynthesisBoundaryType.Word
        event.audio_offset = 1
        event.duration.total_seconds.return_value = 1
        event.text = "Hello"
        event.word_length = 1

        self.tts._callback_word_boundary(event)
        self.assertEqual(len(self.tts._boundaries), 1)

    def test_speak(self):
        with patch.object(self.tts, "_process_callbacks", return_value=[{"text": "hello"}]) as mock_process:
            results = list(self.tts.speak("Hello", "en-US", "happy"))
            self.assertEqual(results, [{"text": "hello"}])


if __name__ == "__main__":
    unittest.main()
