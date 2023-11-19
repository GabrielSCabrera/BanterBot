import unittest
from unittest.mock import patch

from banterbot.extensions.option_selector import OptionSelector
from banterbot.utils.message import Message


class TestOptionSelector(unittest.TestCase):
    """
    This test suite covers the main functionality of the `OptionSelector` class. The `setUp` method initializes an
    instance of `OptionSelector` and the necessary variables for testing. One test method is included `test_select`:
    This test checks if the `select` method returns the expected option for the specified options. It uses the
    `unittest.mock.patch` decorator to mock the `OpenAIService.prompt` method, ensuring that the API is not actually
    called. The test verifies that the returned option matches the expected value and that the `prompt` method is called
    once.

    These tests ensure that the `OptionSelector` class works as expected without making actual API calls.
    """

    def setUp(self):
        self.model = OpenAIModelManager.load("gpt-3.5-turbo")
        self.options = [
            "angry",
            "cheerful",
            "excited",
            "friendly",
            "hopeful",
            "sad",
            "shouting",
            "terrified",
            "unfriendly",
        ]
        self.system = (
            "You are an Emotional Tone Evaluator. Given conversational context, you analyze and select the most "
            "appropriate tone/emotion that the assistant is likely to use next."
        )
        self.prompt = "Choose the most suitable tone/emotion for the assistant's upcoming response."
        self.option_selector = OptionSelector(
            model=self.model, options=self.options, system=self.system, prompt=self.prompt
        )

    @patch("banterbot.extensions.option_selector.OpenAIService.prompt")
    def test_select(self, mock_prompt):
        mock_prompt.return_value = "2"
        messages = [Message(role="user", content="Hello, how are you?")]
        expected_option = "cheerful"

        selected_option = self.option_selector.select(messages=messages)

        self.assertEqual(selected_option, expected_option)
        mock_prompt.assert_called_once()


if __name__ == "__main__":
    unittest.main()
