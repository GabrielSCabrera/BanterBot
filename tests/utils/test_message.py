"""
These unit tests cover different scenarios, including messages with and without names, as well as messages with long
content strings. The expected number of tokens is calculated based on the logic in the count_tokens method.
"""
import unittest

from banterbot.data.constants import ASSISTANT, SYSTEM, USER
from banterbot.data.openai_models import OpenAIModel
from banterbot.utils.message import Message


class MessageTestCase(unittest.TestCase):
    def setUp(self):
        kwargs = {
            "name": "gpt-4",
            "max_tokens": 8192,
            "version": 4,
            "rank": 1,
        }
        self.model = OpenAIModel(**kwargs)  # Create an instance of the OpenAIModel class

    def test_count_tokens_with_name(self):
        # Create a message with a name
        message = Message(role=ASSISTANT, content="Hello!", name="Assistant")
        expected_tokens = 8
        self.assertEqual(message.count_tokens(self.model), expected_tokens)

    def test_count_tokens_without_name(self):
        # Create a message without a name
        message = Message(role=USER, content="Hi!")
        expected_tokens = 7
        self.assertEqual(message.count_tokens(self.model), expected_tokens)

    def test_count_tokens_with_long_content(self):
        # Create a message with a long content string
        content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10
        message = Message(role=SYSTEM, content=content)
        expected_tokens = 106
        self.assertEqual(message.count_tokens(self.model), expected_tokens)


if __name__ == "__main__":
    unittest.main()
