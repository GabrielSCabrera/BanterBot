import os
from typing import Generator, Iterator, List, Union

import openai

from banterbot.data.constants import OPENAI_API_KEY, RETRY_LIMIT
from banterbot.data.openai_models import OpenAIModel
from banterbot.utils.message import Message
from banterbot.utils.nlp import NLP

# Set the OpenAI API key
openai.api_key = os.environ.get(OPENAI_API_KEY)


class OpenAIManager:
    """
    A class that handles the interaction with the OpenAI ChatCompletion API. It provides functionality to generate
    responses from the API based on the input messages. It supports generating responses as a whole or as a stream of
    response blocks.
    """

    def __init__(self, model: OpenAIModel) -> None:
        """
        Initializes an OpenAIManager instance for a specific model.

        Args:
            model (OpenAIModel): The OpenAI model to be used.
        """
        self._model = model

    def _count_tokens(self, messages: List[Message]) -> int:
        """
        Calculates the total number of tokens in the given messages.

        Args:
            messages (List[Message]): A list of messages.

        Returns:
            int: The total number of tokens in the messages.
        """
        num_tokens = 3

        for message in messages:
            num_tokens += message.count_tokens(self._model)

        return num_tokens

    def _response_parse_stream(self, response: Iterator) -> Generator[List[str], None, bool]:
        """
        Parses a streaming response from the OpenAI API and yields blocks of text as they are received.

        Args:
            response (Iterator): The streaming response object.

        Yields:
            Generator[List[str], None, bool]: Lists of sentences as blocks.

        Returns:
            bool: True if the generator completed its iterations, False otherwise (due to interruption).
        """
        self._interrupt = False
        text = ""

        for chunk in response:
            delta = chunk["choices"][0]["delta"]

            if self._interrupt:
                return False

            if "content" in delta.keys():
                text += delta["content"]

            if len(sentences := NLP.segment_sentences(text)) > 1:
                text = sentences[-1]
                yield sentences[:-1]

        sentences = NLP.segment_sentences(text)
        yield sentences

        return True

    def _request(self, messages: List[Message], stream: bool, **kwargs) -> Union[Iterator, str]:
        """
        Sends a request to the OpenAI API and generates a response based on the given parameters.

        Args:
            messages (List[Message]): A list of messages.
            stream (bool): Whether the response should be returned as an iterable stream or a complete text.
            **kwargs: Additional parameters for the API request.

        Returns:
            Union[Iterator, str]: The response from the OpenAI API, either as a stream (Iterator) or text (str).
        """
        kwargs["model"] = self._model.name
        kwargs["n"] = 1
        kwargs["stream"] = stream
        kwargs["messages"] = messages
        kwargs["max_tokens"] = self._model.max_tokens - self._count_tokens(messages=messages)

        success = False
        for i in range(RETRY_LIMIT):
            try:
                response = openai.ChatCompletion.create(**kwargs)
                success = True
                break
            except (openai.error.RateLimitError, openai.error.APIError):
                time.sleep(0.25)

        if not success:
            raise openai.error.APIError

        return response if stream else response.choices[0].message.content.strip()

    def interrupt(self):
        """
        Sets the interruption flag to True, which will stop the streaming response.
        """
        self._interrupt = True

    def prompt(self, messages: List[Message], **kwargs) -> List[str]:
        """
        Sends messages to the OpenAI API and retrieves the response as a list of sentences.

        Args:
            messages (List[Message]): A list of messages.
            **kwargs: Additional parameters for the API request.

        Returns:
            List[str]: A list of sentences forming the response from the OpenAI API.
        """
        response = self._request(messages=messages, stream=False, **kwargs)
        return NLP.segment_sentences(response)

    def prompt_stream(self, messages: List[Message], **kwargs) -> Generator[List[str], None, None]:
        """
        Sends messages to the OpenAI API and retrieves the response as a stream of blocks of sentences.

        Args:
            messages (List[Message]): A list of messages.
            **kwargs: Additional parameters for the API request.

        Yields:
            Generator[List[str], None, None]: A stream of blocks of sentences as the response from the OpenAI API.
        """
        response = self._request(messages=messages, stream=True, **kwargs)

        for block in self._response_parse_stream(response=response):
            yield block
