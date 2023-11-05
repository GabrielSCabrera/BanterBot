import unittest
from typing import Generator
from unittest.mock import MagicMock, patch

from banterbot.data.enums import ChatCompletionRoles
from banterbot.data.openai_models import get_model_by_name
from banterbot.managers.openai_manager import OpenAIManager
from banterbot.utils.message import Message


class TestOpenAIManager(unittest.TestCase):
    """
    This test suite covers the main functionality of the `OpenAIManager` class. The `setUp` method initializes an
    instance of `OpenAIManager` and a list of messages to be used in the tests. The tests cover the following methods:

        1. `test_prompt`: Tests the `prompt` method, ensuring that it returns a list of sentences.
        2. `test_prompt_no_split`: Tests the `prompt` method with the `split` parameter set to `False`, ensuring that it
            returns a single string.
        3. `test_prompt_stream`: Tests the `prompt_stream` method, ensuring that it returns a generator of blocks of
            sentences.
        4. `test_interrupt`: Tests the `interrupt` method, ensuring that the interrupt flag is updated.
        5. `test_streaming`: Tests the `streaming` property, ensuring that it returns the correct streaming state.

    The `openai.ChatCompletion.create` method is mocked using the `unittest.mock` library to simulate API responses
    without making actual API calls.
    """

    def setUp(self):
        self.model = get_model_by_name("gpt-3.5-turbo")
        self.manager = OpenAIManager(self.model)

        self.messages = [
            Message(role=ChatCompletionRoles.SYSTEM, content="You are an AI assistant."),
            Message(role=ChatCompletionRoles.USER, content="What is the capital of France?"),
        ]

    @patch("openai.ChatCompletion.create")
    def test_prompt(self, mock_create):
        mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Paris"))])

        response = self.manager.prompt(self.messages)
        self.assertIsInstance(response, tuple)
        self.assertEqual(response, ("Paris",))

    @patch("openai.ChatCompletion.create")
    def test_prompt_no_split(self, mock_create):
        mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Paris"))])

        response = self.manager.prompt(self.messages, split=False)
        self.assertIsInstance(response, str)
        self.assertEqual(response, "Paris")

    @patch("openai.ChatCompletion.create")
    def test_prompt_stream(self, mock_create):
        mock_create.return_value = iter(
            [
                {"choices": [{"delta": {"content": "The capital"}}]},
                {"choices": [{"delta": {"content": " of France is"}}]},
                {"choices": [{"delta": {"content": " Paris. "}}]},
                {"choices": [{"delta": {"content": "The capital"}}]},
                {"choices": [{"delta": {"content": " of the USA is"}}]},
                {"choices": [{"delta": {"content": " Washington D.C."}}]},
            ]
        )

        response = self.manager.prompt_stream(self.messages)
        self.assertIsInstance(response, Generator)

        blocks = list(response)
        self.assertEqual(
            blocks, [("The capital of France is Paris. ",), ("The capital of the USA is Washington D.C.",)]
        )

    def test_interrupt(self):
        self.manager.interrupt()
        self.assertTrue(self.manager._interrupt > 0)

    def test_streaming(self):
        self.assertFalse(self.manager.streaming)


if __name__ == "__main__":
    unittest.main()
