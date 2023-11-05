import logging
import re
from typing import Optional

from banterbot import config
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.enums import ChatCompletionRoles, Prosody
from banterbot.data.openai_models import OpenAIModel
from banterbot.data.prompts import ProsodySelection
from banterbot.managers.openai_manager import OpenAIManager
from banterbot.utils.message import Message
from banterbot.utils.phrase import Phrase


class ProsodySelector:
    """
    Manages prosody selection/extraction for specified instances of class `AzureNeuralVoice`.
    """

    def __init__(self, model: OpenAIModel, voice: AzureNeuralVoice) -> None:
        """
        Generate a ChatCompletion prompt for the extraction of prosody data for a specified instance of class
        `AzureNeuralVoice`.

        Args:
            model (OpenAIModel): The OpenAI model to be used for generating responses.
            voice (AzureNeuralVoice): An instance of class `AzureNeuralVoice`.
        """
        logging.debug(f"ProsodySelector initialized")
        self._model = model
        self._openai_manager = OpenAIManager(model=self._model)
        self._voice = voice
        self._valid = self._voice.styles is not None

        if self._valid:
            styles = "\n".join([f"{n+1:02d} {i}" for n, i in enumerate(self._voice.styles)])
            styledegrees = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.STYLEDEGREES.keys())])
            pitches = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.PITCHES.keys())])
            rates = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.RATES.keys())])
            emphases = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.EMPHASES.keys())])

            self._system_processed = "\n".join(
                [
                    ProsodySelection.PREFIX.value,
                    ProsodySelection.STYLE.value,
                    styles,
                    ProsodySelection.STYLEDEGREE.value,
                    styledegrees,
                    ProsodySelection.PITCH.value,
                    pitches,
                    ProsodySelection.RATE.value,
                    rates,
                    ProsodySelection.EMPHASIS.value,
                    emphases,
                    ProsodySelection.SUFFIX.value,
                    ProsodySelection.EXAMPLE.value,
                ]
            )

    def select(
        self,
        sentences: list[str],
        messages: Optional[list[Message]] = None,
        messages_token_count: Optional[list[int]] = None,
        content: Optional[str] = None,
        character: Optional[str] = None,
    ) -> str:
        """
        Extract prosody settings for a list of sentences divided into sub-sentences by asking the OpenAI ChatCompletion
        API to pick a set of options. The prompt is set up to force the model to return an exact number of tokens with
        dummy text preceding it in order to yield consistent results efficiently.

        Args:
            sentences (list[str]): The list of sentences to be processed.
            messages (optional, list[Message]): A list of messages that can be used as conversation context.
            messages_token_count (optional, list[int]): A list of the token count for each message.
            content (optional, str): Any text send prior to the current one, but not yet registered in the messages.
            character (optional, str): A description of the character to assist the ChatCompletion in picking reactions.

        Returns:
            str: The randomly selected option.
        """
        phrases = self._split_sentences(sentences)
        messages = self._get_messages(phrases, messages, messages_token_count, content, character)
        response = self._openai_manager.prompt(
            messages=messages, split=False, temperature=0.0, top_p=1.0, max_tokens=self._max_tokens(len(phrases))
        )
        return self._process_response(phrases, response)

    def _max_tokens(self, N: int) -> int:
        """
        Return the maximum number of tokens for the given number of rows of six-digit numbers.
        """
        dummy = "012345\n" * N
        return len(self._model.tokenizer.encode(dummy))

    def _get_messages(
        self,
        phrases: list[str],
        messages: Optional[list[Message]] = None,
        messages_token_count: Optional[list[int]] = None,
        content: Optional[str] = None,
        character: Optional[str] = None,
    ) -> list[Message]:
        """
        Insert the system prompt, user prompt, prefix, suffix, and a dummy message mimicking a successful interaction
        with the ChatCompletion API, into the list of messages.

        Args:
            phrases (list[str]): The list of phrases to be processed.
            messages (optional, list[Message]): A list of messages that can be used as conversation context.
            messages_token_count (optional, list[int]): A list of the token count for each message.
            content (optional, str): Any text send prior to the current one, but not yet registered in the messages.
            character (optional, str): A description of the character to assist the ChatCompletion in picking reactions.

        Returns:
            list[Message]: The enhanced list of messages.
        """
        phrases_numbered = "\n".join(phrases)

        system = Message(role=ChatCompletionRoles.SYSTEM, content=self._system_processed)
        character = Message(role=ChatCompletionRoles.SYSTEM, content=character)
        prompt = Message(
            role=ChatCompletionRoles.USER, content=ProsodySelection.PROMPT.value.format(len(phrases), phrases_numbered)
        )
        dummy_message = Message(
            role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.DUMMY.value.format(len(phrases))
        )
        return [system, character, prompt, dummy_message]

    def _process_response(self, phrases: list[str], response: str) -> list[Phrase]:
        """
        Given a response from the ChatCompletion API using the `_prompt` instance attribute, parses one sub-sentence and
        returns an instance of class `Phrase`.

        Args:
            phrases (str): The string divided into sub-sentences (phrases).
            response (str): The ChatCompletion response to be processed.

        Returns:
            list[Phrase]: A processed list of instances of class `Phrase`.
        """
        output = []
        responses = response.strip().split("\n")
        for phrase, response in zip(phrases, responses):
            print(response)
            if response.strip():
                output.append(
                    Phrase(
                        text=phrase,
                        style=self._voice.styles[min(int(response[:2]), len(self._voice.styles)) - 1],
                        styledegree=list(Prosody.STYLEDEGREES.values())[min(int(response[2]), len(Prosody.STYLEDEGREES)) - 1],
                        pitch=list(Prosody.PITCHES.values())[min(int(response[3]), len(Prosody.PITCHES)) - 1],
                        rate=list(Prosody.RATES.values())[min(int(response[4]), len(Prosody.RATES)) - 1],
                        emphasis=list(Prosody.EMPHASES.values())[min(int(response[5]), len(Prosody.EMPHASES)) - 1],
                        voice=self._voice,
                    )
                )
        return output

    def _split_sentences(self, sentences: list[str]) -> tuple[list[str], int]:
        """
        Given a list of sentences, splits them on certain types of punctuation (defined in `config.py`) into smaller
        phrases.

        Args:
            sentences (list[Message]): The list of sentences to be processed.

        Returns:
            list[str]: A list of sub-sentences divided on the specified punctuation delimiters.
            int: The number of tokens expected in the ChatCompletion response.
        """
        phrases = []

        for sentence in sentences:
            result = re.split(config.phrase_delim_pattern, sentence)
            processed = []
            for n, phrase in enumerate(result):
                if phrase.strip():
                    if n % 2 == 0 or len(processed) == 0:
                        processed.append(phrase)
                    else:
                        processed[-1] += phrase
            phrases += processed

        return phrases
