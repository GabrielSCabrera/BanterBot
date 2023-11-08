import logging
import re
from typing import Optional

from banterbot.config import RETRY_LIMIT
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.enums import ChatCompletionRoles, Prosody
from banterbot.data.openai_models import OpenAIModel
from banterbot.data.prompts import ProsodySelection
from banterbot.managers.openai_manager import OpenAIManager
from banterbot.utils.exceptions import FormatMismatchError
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
        self._token_counts = {}
        self._output_patterns = {}
        self._init_system()

    def _init_system(self) -> None:
        """
        Prepare the system prompt on instantiation, which is customized on a model-to-model basis, since different
        `OpenAIModel` instances vary in terms of available styles. Also prepares a regex pattern that matches one line
        of expected output for the current model.
        """
        # Convert the different prosody options into
        styles = "\n".join([f"{n+1:02d} {i}" for n, i in enumerate(self._voice.styles)])
        styledegrees = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.STYLEDEGREES)])
        pitches = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.PITCHES)])
        rates = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.RATES)])
        emphases = "\n".join([f"{n+1} {i}" for n, i in enumerate(Prosody.EMPHASES)])

        self._system = [
            Message(role=ChatCompletionRoles.SYSTEM, content=ProsodySelection.PREFIX.value),
            Message(role=ChatCompletionRoles.USER, content=ProsodySelection.STYLE_USER.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.STYLE_ASSISTANT.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=styles),
            Message(role=ChatCompletionRoles.USER, content=ProsodySelection.STYLEDEGREE_USER.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.STYLEDEGREE_ASSISTANT.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=styledegrees),
            Message(role=ChatCompletionRoles.USER, content=ProsodySelection.PITCH_USER.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.PITCH_ASSISTANT.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=pitches),
            Message(role=ChatCompletionRoles.USER, content=ProsodySelection.RATE_USER.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.RATE_ASSISTANT.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=rates),
            Message(role=ChatCompletionRoles.USER, content=ProsodySelection.EMPHASIS_USER.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.EMPHASIS_ASSISTANT.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=emphases),
            Message(
                role=ChatCompletionRoles.USER,
                content=ProsodySelection.SUFFIX.value.format(
                    style=len(self._voice.styles),
                    styledegree=len(Prosody.STYLEDEGREES),
                    pitch=len(Prosody.PITCHES),
                    rate=len(Prosody.RATES),
                    emphasis=len(Prosody.EMPHASES),
                ),
            ),
            Message(role=ChatCompletionRoles.USER, content=ProsodySelection.EXAMPLE_USER.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.EXAMPLE_ASSISTANT_1.value),
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.EXAMPLE_ASSISTANT_2.value),
        ]

        # Given the possible ranges of Prosody settings, generate a regex pattern that asserts valid settings.
        self._line_pattern = (
            f"[0-{len(self._voice.styles) // 10}][1-{min(len(self._voice.styles), 9)}]"
            f"[1-{len(Prosody.STYLEDEGREES)}]"
            f"[1-{len(Prosody.PITCHES)}]"
            f"[1-{len(Prosody.RATES)}]"
            f"[1-{len(Prosody.EMPHASES)}]"
        )

    def select(self, sentences: list[str], context: Optional[str] = None, system: Optional[str] = None) -> str:
        """
        Extract prosody settings for a list of sentences divided into sub-sentences by asking the OpenAI ChatCompletion
        API to pick a set of options. The prompt is set up to force the model to return an exact number of tokens with
        dummy text preceding it in order to yield consistent results efficiently.

        Args:
            sentences (list[str]): The list of sentences to be processed.
            context (optional, str): Useful prior conversational context originating from the same response.
            system (optional, str): A system prompt to assist the ChatCompletion in picking reactions.

        Returns:
            str: The randomly selected option.
        """

        for i in range(RETRY_LIMIT):

            # Attempt three different sentence splits in order to modify the input on retry -- this reduces the chance
            # of a `FormatMismatchError` Exception significantly.
            if i == 0:
                phrases = self._split_sentences(sentences)
                messages = self._get_messages(phrases, context, system)
            elif i == 1:
                phrases = " ".join(sentences).split(".")
                messages = self._get_messages(phrases, context, system)
            else:
                phrases = [" ".join(sentences)]
                messages = self._get_messages(phrases, context, system)

            response = self._openai_manager.prompt(
                messages=messages,
                split=False,
                temperature=0.0,
                top_p=1.0,
                max_tokens=self._get_max_tokens(len(phrases)),
            )
            processed, outputs = self._process_response(phrases, response)

            if processed is not None:
                break
            elif i + 1 == RETRY_LIMIT:
                raise FormatMismatchError()

        return processed, outputs

    def _get_max_tokens(self, N: int) -> int:
        """
        Return the maximum number of tokens for the given number of rows of six-digit numbers. Caches all calculated
        values.
        """
        # Count the number of tokens for the specified `N`.
        if N not in self._token_counts:
            dummy = "012345\n" * (N - 1) + "012345"
            self._token_counts[N] = len(self._model.tokenizer.encode(dummy))

        return self._token_counts[N]

    def _get_output_pattern(self, N: int) -> int:
        """
        Return a compiled regex pattern matching the expected ChatCompletion output for a given `N`, or number of
        phrases. Caches all calculated values.
        """
        # Compile a regex pattern that matches `N` lines of expected output from ChatCompletion's prosody evaluation.
        if N not in self._output_patterns:
            self._output_patterns[N] = re.compile(f"{self._line_pattern}\n" * (N - 1) + self._line_pattern)

        return self._output_patterns[N]

    def _get_messages(
        self, phrases: list[str], context: Optional[str] = None, system: Optional[str] = None
    ) -> list[Message]:
        """
        Insert the system prompt, user prompt, prefix, suffix, and a dummy message mimicking a successful interaction
        with the ChatCompletion API, into the list of messages.

        Args:
            phrases (list[str]): The list of phrases to be processed.
            context (optional, str): Useful prior conversational context originating from the same response.
            system (optional, str): A system prompt to assist the ChatCompletion in picking reactions.

        Returns:
            list[Message]: The enhanced list of messages.
        """
        messages = self._system.copy()

        if not system:
            messages.append(
                Message(role=ChatCompletionRoles.SYSTEM, content=ProsodySelection.CHARACTER.value.format(system))
            )

        if not context:
            messages.append(
                Message(role=ChatCompletionRoles.SYSTEM, content=ProsodySelection.CONTEXT.value.format(context))
            )

        messages.append(
            Message(
                role=ChatCompletionRoles.USER,
                content=ProsodySelection.PROMPT.value.format(len(phrases), "\n".join(phrases)),
            )
        )
        messages.append(
            Message(role=ChatCompletionRoles.ASSISTANT, content=ProsodySelection.DUMMY.value.format(len(phrases)))
        )

        return messages

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
        processed = []
        pattern = self._get_output_pattern(len(phrases))
        if re.fullmatch(pattern, response) is not None:
            outputs = re.findall(self._get_output_pattern(1), response)
            for output, phrase in zip(outputs, phrases):
                processed.append(
                    Phrase(
                        text=phrase,
                        style=self._voice.styles[min(int(response[:2]), len(self._voice.styles)) - 1],
                        styledegree=list(Prosody.STYLEDEGREES.values())[int(response[2]) - 1],
                        pitch=list(Prosody.PITCHES.values())[int(response[3]) - 1],
                        rate=list(Prosody.RATES.values())[int(response[4]) - 1],
                        emphasis=list(Prosody.EMPHASES.values())[int(response[5]) - 1],
                        voice=self._voice,
                    )
                )
            return processed, outputs
        else:
            return None, None

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
            result = re.split(Prosody.PHRASE_PATTERN, sentence)
            processed = []
            for n, phrase in enumerate(result):
                if phrase := phrase.strip():
                    if (not re.match(Prosody.PHRASE_PATTERN, phrase) and phrase.count(" ") > 1) or not processed:
                        processed.append(phrase)
                    else:
                        processed[-1] += phrase
            phrases += processed

        return phrases
