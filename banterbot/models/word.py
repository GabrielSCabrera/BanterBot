import datetime
from dataclasses import dataclass
from typing import Optional

import azure.cognitiveservices.speech as speechsdk

from banterbot.data.enums import SpeechProcessingType


@dataclass(frozen=True)
class Word:
    """
    This class encapsulates a word in the output of a text-to-speech synthesis or input from a speech-to-text
    recognition. It includes the word itself and the timestamp when the word was spoken. Optionally, its category (e.g.,
    word, punctuation using Azure's Speech Synthesis Boundary Type), and its confidence score can be included too.

    Attributes:
        word (str): The word that has been synthesized/recognized.
        offset (datetime.timedelta): Time elapsed between initialization and synthesis/recognition.
        duration (datetime.timedelta): Amount of time required for the word to be fully spoken.
        category (speechsdk.SpeechSynthesisBoundaryType): The category of the text contents.
        confidence (Optional[int]): The confidence score (for speech-to-text) for the specified word.
        source: SpeechProcessingType: Whether the word's source is text-to-speech (TTS) or speech-to-text (STT).
    """

    word: str
    offset: datetime.timedelta
    duration: datetime.timedelta
    category: speechsdk.SpeechSynthesisBoundaryType
    source: SpeechProcessingType
    confidence: Optional[float] = None

    def __len__(self) -> int:
        """
        Computes and returns the length of the word.

        This method is useful for determining the length of the word without having to access the `word` attribute
        directly. It can be used, for example, in filtering or sorting operations on a list of `Word`
        instances.

        Returns:
            int: The length of the word.
        """
        return len(self.word)

    def __str__(self) -> str:
        """
        Provides a string representation of the instance, including the word and its timestamp.

        This method is useful for displaying a human-readable representation of the instance, which can be helpful for
        debugging or logging purposes.

        Returns:
            str: A string containing the word, the time elapsed since the beginning of speech synthesis, and its source.
        """
        description = (
            "<"
            f"word: `{self.word}` "
            f"| offset: {self.offset.seconds}s "
            f"| duration: {self.duration.seconds}s "
            f"| source: {self.source.name}"
            ">"
        )
        return description

    def __repr__(self) -> str:
        """
        Returns the word itself as its string representation. This simplifies the display of the object in certain
        contexts, such as when printing a list of `Word` instances.

        This method is called by built-in Python functions like `repr()` and is used, for example, when displaying the
        object in an interactive Python session or when printing a list containing the object.

        Returns:
            str: The word itself.
        """
        return self.word
