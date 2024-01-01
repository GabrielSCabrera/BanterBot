import unittest
from dataclasses import dataclass
from unittest.mock import patch

from banterbot.models.message import Message
from banterbot.models.openai_model import OpenAIModel
from banterbot.services.openai_service import OpenAIService


@dataclass
class Content:
    content: str


@dataclass
class Delta:
    delta: Content


@dataclass
class Value:
    choices: list[Delta]


class TestOpenAIService(unittest.TestCase):
    def setUp(self):
        self.model = OpenAIModel(model="gpt-3.5-turbo", max_tokens=100, generation=1, rank=1)
        self.service = OpenAIService(self.model)

    def test_count_tokens(self):
        string = "Hello, world!"
        expected_tokens = 4

        tokens = self.service.count_tokens(string)

        self.assertEqual(tokens, expected_tokens)

    def test_prompt(self):
        messages = [
            Message(content="What is the weather today?", role="user"),
            Message(content="I'm not sure, let me check.", role="assistant"),
        ]
        expected_response = "The weather is sunny."

        with patch.object(OpenAIService, "_request", return_value=expected_response):
            response = self.service.prompt(messages, split=False)
            response_split = self.service.prompt(messages, split=True)

        self.assertEqual(response, expected_response)
        self.assertEqual(response_split, (expected_response,))

    def test_prompt_stream(self):
        messages = [
            Message(content="Tell me a joke.", role="user"),
            Message(content="Why don't scientists trust atoms?", role="assistant"),
        ]
        expected_response = ["Because...", " they make up everything."]
        output = [Value([Delta(Content(i))]) for i in expected_response]
        expected_response = [("".join(expected_response),)]

        with patch.object(OpenAIService, "_request", return_value=output):
            handler = self.service.prompt_stream(messages)
            response = list(handler)

        self.assertEqual(response, expected_response)


if __name__ == "__main__":
    unittest.main()
