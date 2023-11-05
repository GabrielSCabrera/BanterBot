import math
import re

from banterbot import config
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.enums import ChatCompletionRoles, Prosody
from banterbot.data.openai_models import OpenAIModel
from banterbot.managers.openai_manager import OpenAIManager
from banterbot.data.prompts import ProsodySelection
from banterbot.utils.message import Message
from banterbot.utils.phrase import Phrase
import logging

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
            styledegrees = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.STYLEDEGREES)])
            pitches = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.PITCHES)])
            rates = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.RATES)])
            emphases = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.EMPHASES)])

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

    def select(self, sentences: list[str]) -> str:
        """
        Extract prosody settings for a list of sentences divided into sub-sentences by asking the OpenAI ChatCompletion
        API to pick a set of options. The prompt is set up to force the model to return an exact number of tokens with
        dummy text preceding it in order to yield consistent results efficiently.

        Args:
            sentences (list[Message]): The list of sentences to be processed.

        Returns:
            str: The randomly selected option.
        """
        phrases = None
        if self._valid:
            phrases, max_tokens = self._split_sentences(sentences)
            messages = self._get_messages(phrases)
            response = self._openai_manager.prompt(
                messages=messages, split=False, temperature=0.0, top_p=1.0, max_tokens=max_tokens
            )
            try:
                phrases = self._process_response(phrases, response)
            except:
                logging.debug(f"ProsodySelector was unable to process a response: `{response}`")

        return phrases

    def _get_messages(self, phrases: list[str]) -> list[Message]:
        """
        Insert the system prompt, user prompt, prefix, suffix, and a dummy message mimicking a successful interaction
        with the ChatCompletion API, into the list of messages.

        Args:
            phrases (list[Message]): The list of phrases to be processed.

        Returns:
            list[Message]: The enhanced list of messages.
        """
        phrases_numbered = "\n".join([f"{n+1} {i}" for n, i in enumerate(phrases)])
        system = Message(role=ChatCompletionRoles.SYSTEM, content=self._system_processed)
        prompt = Message(
            role=ChatCompletionRoles.USER, content=ProsodySelection.PROMPT.value.format(len(phrases), phrases_numbered)
        )
        dummy_message = Message(
            role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.DUMMY.value.format(len(phrases))
        )
        return [system, prompt, dummy_message]

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
            output.append(
                Phrase(
                    text=phrase,
                    style=self._voice.styles[int(phrase[:2] - 1)],
                    styledegree=Prosody.STYLEDEGREES[int(phrase[2] - 1)],
                    pitch=Prosody.PITCHES[int(phrase[3] - 1)],
                    rate=Prosody.RATES[int(phrase[4] - 1)],
                    emphasis=Prosody.EMPHASES[int(phrase[5] - 1)],
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
        max_tokens = 0
        counter = 0

        for sentence in sentences:
            result = re.split("([" + "".join(config.phrase_delim) + "])", sentence)
            processed = []
            for n, phrase in enumerate(result):
                if n % 2 == 0:
                    processed.append(phrase)
                else:
                    processed[-1] += phrase
            phrases += processed
            counter += 1
            max_tokens += 3 + int(math.log10(counter))

        return phrases, max_tokens
