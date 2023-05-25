import datetime
from dataclasses import dataclass

import azure.cognitiveservices.speech as speechsdk


@dataclass(frozen=True)
class TextToSpeechWord:
    """
    This class encapsulates a word in the output of a text-to-speech conversion. It includes
    the word itself, the timestamp when the word was spoken, its index in the text, and its category
    (e.g., word, punctuation), using Azure's Speech Synthesis Boundary Type.
    """

    # The word that has been converted to speech
    word: str
    # The datetime when the word was spoken
    timestamp: datetime.datetime
    # The position of the word in the original text
    word_index: int
    # The category of the word (e.g., word, punctuation)
    category: speechsdk.SpeechSynthesisBoundaryType

    def __len__(self) -> int:
        """
        Computes and returns the length of the word.

        Returns:
            int: The length of the word.
        """
        return len(self.word)

    def __str__(self) -> str:
        """
        Provides a string representation of the instance, including the word and its timestamp.

        Returns:
            str: A string containing the word and its timestamp in ISO 8601 format.
        """
        description = f"<TextToSpeechWord '{self.word}' at {self.timestamp.isoformat()}>"
        return description

    def __repr__(self) -> str:
        """
        Returns the word itself as its string representation. This simplifies the display of
        the object in certain contexts.

        Returns:
            str: The word itself.
        """
        return self.word
