import os
import time
from typing import Generator, Iterator, List, Union

import openai

from banterbot.data.config import RETRY_LIMIT
from banterbot.data.enums import EnvVar
from banterbot.data.openai_models import OpenAIModel
from banterbot.utils.message import Message
from banterbot.utils.nlp import NLP

# Set the OpenAI API key
openai.api_key = os.environ.get(EnvVar.OPENAI_API_KEY.value)


class OpenAIManager:
    """
    A class that handles the interaction with the OpenAI ChatCompletion API. It provides functionality to generate
    responses from the API based on the input messages. It supports generating responses as a whole or as a stream of
    response blocks.

    The main purpose of this class is to facilitate the communication with the OpenAI API and manage the responses
    generated by the API. It can be used to create chatbots or other applications that require natural language
    processing and generation.
    """

    def __init__(self, model: OpenAIModel) -> None:
        """
        Initializes an OpenAIManager instance for a specific model.

        Args:
            model (OpenAIModel): The OpenAI model to be used. This should be an instance of the OpenAIModel class, which
            contains information about the model, such as its name and maximum token limit.
        """
        self._model = model
        self._streaming = False

    def prompt(self, messages: List[Message], **kwargs) -> List[str]:
        """
        Sends messages to the OpenAI ChatCompletion API and retrieves the response as a list of sentences.

        Args:
            messages (List[Message]): A list of messages. Each message should be an instance of the Message class, which
            contains the content and role (user or assistant) of the message.

            **kwargs: Additional parameters for the API request. These can include settings such as temperature, top_p,
            and frequency_penalty.

        Returns:
            List[str]: A list of sentences forming the response from the OpenAI API. This can be used to display
            the generated response to the user or for further processing.
        """
        response = self._request(messages=messages, stream=False, **kwargs)
        return NLP.segment_sentences(response)

    def prompt_stream(self, messages: List[Message], **kwargs) -> Generator[List[str], None, None]:
        """
        Sends messages to the OpenAI API and retrieves the response as a stream of blocks of sentences.

        Args:
            messages (List[Message]): A list of messages. Each message should be an instance of the Message class, which
            contains the content and role (user or assistant) of the message.

            **kwargs: Additional parameters for the API request. These can include settings such as temperature, top_p,
            and frequency_penalty.

        Yields:
            Generator[List[str], None, None]: A stream of blocks of sentences as the response from the OpenAI API. Each
            block contains one or more sentences that form a part of the generated response. This can be used to display
            the response to the user in real-time or for further processing.
        """
        # Obtain a response from the OpenAI ChatCompletion API
        response = self._request(messages=messages, stream=True, **kwargs)

        # Set the streaming flag to True
        self._streaming = True

        # Yield the responses as they are streamed
        for block in self._response_parse_stream(response=response):
            yield block

        # Reset the streaming flag to False
        self._streaming = False

    def interrupt(self) -> None:
        """
        Sets the interruption flag to True, which will stop the streaming response. This can be used to manually
        interrupt the streaming response if needed, for example, if the user sends a new message before the current
        response is completed.
        """
        self._interrupt = True

    @property
    def streaming(self) -> bool:
        """
        If the current instance of OpenAIManager is in the process of streaming, returns True. Otherwise, returns False.

        Args:
            bool: The streaming state of the current instance.
        """
        return self._streaming

    def _count_tokens(self, messages: List[Message]) -> int:
        """
        Calculates the total number of tokens in the given messages.

        Args:
            messages (List[Message]): A list of messages. Each message should be an instance of the Message class, which
            contains the content and role (user or assistant) of the message.

        Returns:
            int: The total number of tokens in the messages. This is used to ensure that the generated response does not
            exceed the model's maximum token limit.
        """
        num_tokens = 3

        for message in messages:
            num_tokens += message.count_tokens(self._model)

        return num_tokens

    def _request(self, messages: List[Message], stream: bool, **kwargs) -> Union[Iterator, str]:
        """
        Sends a request to the OpenAI API and generates a response based on the given parameters.

        Args:
            messages (List[Message]): A list of messages. Each message should be an instance of the Message class, which
            contains the content and role (user or assistant) of the message.

            stream (bool): Whether the response should be returned as an iterable stream or a complete text.

            **kwargs: Additional parameters for the API request. These can include settings such as temperature, top_p,
            and frequency_penalty.

        Returns:
            Union[Iterator, str]: The response from the OpenAI API, either as a stream (Iterator) or text (str).
        """
        kwargs["model"] = self._model.name
        kwargs["n"] = 1
        kwargs["stream"] = stream
        kwargs["messages"] = [message() for message in messages]
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

    def _response_parse_stream(self, response: Iterator) -> Generator[List[str], None, bool]:
        """
        Parses a streaming response from the OpenAI API and yields blocks of text as they are received.

        Args:
            response (Iterator): The streaming response object. This is the raw response received from the OpenAI API
            when requesting a streaming response.

        Yields:
            Generator[List[str], None, bool]: Lists of sentences as blocks. Each block contains one or more sentences
            that form a part of the generated response.

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
