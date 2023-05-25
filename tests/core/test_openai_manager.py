"""
These tests cover various aspects of the OpenAIManager class, including token counting, response stream parsing, making
requests to the OpenAI API, sending prompts, and streaming responses. Mock objects are used to simulate the behavior of
the OpenAI API for testing purposes.
"""
import os
import time
import unittest
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import patch

import openai

from banterbot.core.openai_manager import OpenAIManager
from banterbot.data.openai_models import OpenAIModel
from banterbot.utils.message import Message
from banterbot.utils.nlp import NLP


@dataclass
class MockContent:
    content: str


@dataclass
class MockChoice:
    message: str

    def __post_init__(self):
        self.message = MockContent(self.message["delta"]["content"])


class MockOpenAICompletion:
    def __init__(self, choices):
        self.choices = [MockChoice(choice) for choice in choices]
        self.idx = 0

    def __next__(self):
        if self.idx < len(self.choices):
            self.idx += 1
            return self.choices[self.idx - 1]
        else:
            raise StopIteration

    def __iter__(self):
        self.idx = 0
        return self


class MockOpenAICompletionStream:
    def __init__(self, choices):
        self.choices = choices
        self.idx = 0

    def __next__(self):
        if self.idx < len(self.choices):
            self.idx += 1
            return self.choices[self.idx - 1]
        else:
            raise StopIteration

    def __iter__(self):
        self.idx = 0
        return self


class OpenAIManagerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        kwargs = {
            "name": "gpt-4",
            "max_tokens": 8192,
            "version": 4,
            "rank": 1,
        }
        self.model = OpenAIModel(**kwargs)

    def test_count_tokens(self):
        message1 = Message(role="user", content="Hello")
        message2 = Message(role="assistant", content="Hi", name="Assistant")
        messages = [message1, message2]
        manager = OpenAIManager(model=self.model)
        token_count = manager._count_tokens(messages)
        self.assertEqual(token_count, 16)

    def test_response_parse_stream(self):
        response = [
            {"choices": [{"delta": {"content": "Hello,"}}]},
            {"choices": [{"delta": {"content": " how"}}]},
            {"choices": [{"delta": {"content": " are"}}]},
            {"choices": [{"delta": {"content": " you?"}}]},
            {"choices": [{"delta": {"content": " Fine..."}}]},
            {"choices": [{"delta": {"content": " thanks,"}}]},
            {"choices": [{"delta": {"content": " how"}}]},
            {"choices": [{"delta": {"content": " about"}}]},
            {"choices": [{"delta": {"content": " you"}}]},
            {"choices": [{"delta": {"content": " Mr."}}]},
            {"choices": [{"delta": {"content": " Smith?"}}]},
        ]
        manager = OpenAIManager(model=self.model)
        stream = manager._response_parse_stream(response)
        block1 = next(stream)
        self.assertEqual(block1, ("Hello, how are you?",))
        block2 = next(stream)
        self.assertEqual(block2, ("Fine... thanks, how about you Mr. Smith?",))
        with self.assertRaises(StopIteration):
            next(stream)

    def test_request_stream(self):
        message = Message(role="user", content="Hello")
        messages = [message]
        manager = OpenAIManager(model=self.model)

        def mock_create(*args, **kwargs):
            response = [
                {"choices": [{"delta": {"content": "Hello,"}}]},
                {"choices": [{"delta": {"content": " how"}}]},
                {"choices": [{"delta": {"content": " are"}}]},
                {"choices": [{"delta": {"content": " you?"}}]},
            ]
            return MockOpenAICompletionStream(response)

        with patch.object(openai.ChatCompletion, "create", side_effect=mock_create):
            stream = manager._request(messages=messages, stream=True)
            block1 = next(stream)
            self.assertEqual(block1, {"choices": [{"delta": {"content": "Hello,"}}]})
            block2 = next(stream)
            self.assertEqual(block2, {"choices": [{"delta": {"content": " how"}}]})
            block3 = next(stream)
            self.assertEqual(block3, {"choices": [{"delta": {"content": " are"}}]})
            block4 = next(stream)
            self.assertEqual(block4, {"choices": [{"delta": {"content": " you?"}}]})
            with self.assertRaises(StopIteration):
                next(stream)

    def test_prompt_stream_interrupt(self):
        message = Message(role="user", content="Hello")
        messages = [message]
        manager = OpenAIManager(model=self.model)

        def mock_create(*args, **kwargs):
            response = [
                {"choices": [{"delta": {"content": "Hello,"}}]},
                {"choices": [{"delta": {"content": " how"}}]},
                {"choices": [{"delta": {"content": " are"}}]},
                {"choices": [{"delta": {"content": " you?"}}]},
                {"choices": [{"delta": {"content": " Fine..."}}]},
                {"choices": [{"delta": {"content": " thanks,"}}]},
                {"choices": [{"delta": {"content": " how"}}]},
                {"choices": [{"delta": {"content": " about"}}]},
                {"choices": [{"delta": {"content": " you"}}]},
                {"choices": [{"delta": {"content": " Mr."}}]},
                {"choices": [{"delta": {"content": " Smith?"}}]},
            ]
            return MockOpenAICompletionStream(response)

        with patch.object(openai.ChatCompletion, "create", side_effect=mock_create):
            stream = manager.prompt_stream(messages=messages)

            block1 = next(stream)
            self.assertEqual(block1, ("Hello, how are you?",))
            manager.interrupt()
            with self.assertRaises(StopIteration):
                next(stream)

    def test_request_no_stream(self):
        message = Message(role="user", content="Hello")
        messages = [message]
        manager = OpenAIManager(model=self.model)

        def mock_create(*args, **kwargs):
            response = MockOpenAICompletion([{"delta": {"content": "Hello, how are you?"}}])
            return response

        with patch.object(openai.ChatCompletion, "create", side_effect=mock_create):
            response = manager._request(messages=messages, stream=False)
            self.assertEqual(response, "Hello, how are you?")

    def test_prompt(self):
        message = Message(role="user", content="Hello")
        messages = [message]
        manager = OpenAIManager(model=self.model)

        def mock_create(*args, **kwargs):
            response = MockOpenAICompletion([{"delta": {"content": "Hello, how are you?"}}])
            return response

        with patch.object(openai.ChatCompletion, "create", side_effect=mock_create):
            sentences = manager.prompt(messages=messages)
            self.assertEqual(sentences, ("Hello, how are you?",))

    def test_prompt_stream(self):
        message = Message(role="user", content="Hello")
        messages = [message]
        manager = OpenAIManager(model=self.model)

        def mock_create(*args, **kwargs):
            response = [
                {"choices": [{"delta": {"content": "Hello,"}}]},
                {"choices": [{"delta": {"content": " how"}}]},
                {"choices": [{"delta": {"content": " are"}}]},
                {"choices": [{"delta": {"content": " you?"}}]},
                {"choices": [{"delta": {"content": " Fine..."}}]},
                {"choices": [{"delta": {"content": " thanks,"}}]},
                {"choices": [{"delta": {"content": " how"}}]},
                {"choices": [{"delta": {"content": " about"}}]},
                {"choices": [{"delta": {"content": " you"}}]},
                {"choices": [{"delta": {"content": " Mr."}}]},
                {"choices": [{"delta": {"content": " Smith?"}}]},
            ]
            return MockOpenAICompletionStream(response)

        with patch.object(openai.ChatCompletion, "create", side_effect=mock_create):
            stream = manager.prompt_stream(messages=messages)

            block1 = next(stream)
            self.assertEqual(block1, ("Hello, how are you?",))
            block2 = next(stream)
            self.assertEqual(block2, ("Fine... thanks, how about you Mr. Smith?",))
            with self.assertRaises(StopIteration):
                next(stream)


if __name__ == "__main__":
    unittest.main()
