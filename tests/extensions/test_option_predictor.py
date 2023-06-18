import unittest
from unittest.mock import patch

from banterbot.data.openai_models import OpenAIModel, get_model_by_name
from banterbot.extensions.option_predictor import OptionPredictor
from banterbot.utils.message import Message


class TestOptionPredictor(unittest.TestCase):
    """
    This test suite covers the main functionality of the `OptionPredictor` class. The `setUp` method initializes an
    instance of `OptionPredictor` and the necessary variables for testing. Two test methods are included:

        1. `test_evaluate`: This test checks if the `evaluate` method returns the expected probabilities for the given
            options. It uses the `unittest.mock.patch` decorator to mock the `OpenAIManager.prompt` method, ensuring
            that the API is not actually called. The test verifies that the returned probabilities match the expected
            values and that the `prompt` method is called once.

        2. `test_random_select`: This test checks if the `random_select` method returns a valid option from the given
            options. It also uses the `unittest.mock.patch` decorator to mock the `OpenAIManager.prompt` method. The
            test verifies that the selected option is in the list of options and that the `prompt` method is called
            once.

    These tests ensure that the `OptionPredictor` class works as expected without making actual API calls.
    """

    def setUp(self):
        self.model = get_model_by_name("gpt-3.5-turbo")
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
            "You are an Emotional Tone Evaluator. Given conversational context, you analyze and assign probabilities "
            "to a set of tones/emotions that the assistant is likely to use next."
        )
        self.prompt = "Analyze the probabilities of different tones/emotions for the assistant's upcoming response."
        self.seed = 42
        self.option_predictor = OptionPredictor(
            model=self.model, options=self.options, system=self.system, prompt=self.prompt, seed=self.seed
        )

    @patch("banterbot.extensions.option_predictor.OpenAIManager.prompt")
    def test_evaluate(self, mock_prompt):
        mock_prompt.return_value = (
            "angry:0\ncheerful:50\nexcited:20\nfriendly:10\nhopeful:10\nsad:5\nshouting:0\nterrified:0\nunfriendly:5"
        )
        messages = [Message(role="user", content="Hello, how are you?")]
        expected_probabilities = {
            "angry": 0.0,
            "cheerful": 0.5,
            "excited": 0.2,
            "friendly": 0.1,
            "hopeful": 0.1,
            "sad": 0.05,
            "shouting": 0.0,
            "terrified": 0.0,
            "unfriendly": 0.05,
        }

        probabilities = self.option_predictor.evaluate(messages=messages)

        self.assertEqual(probabilities, expected_probabilities)
        mock_prompt.assert_called_once()

    @patch("banterbot.extensions.option_predictor.OpenAIManager.prompt")
    def test_random_select(self, mock_prompt):
        mock_prompt.return_value = (
            "angry:0\ncheerful:50\nexcited:20\nfriendly:10\nhopeful:10\nsad:5\nshouting:0\nterrified:0\nunfriendly:5"
        )
        messages = [Message(role="user", content="Hello, how are you?")]

        selected_option = self.option_predictor.random_select(messages=messages)

        self.assertIn(selected_option, self.options)
        mock_prompt.assert_called_once()


if __name__ == "__main__":
    unittest.main()
