import datetime
from dataclasses import dataclass

import azure.cognitiveservices.speech as speechsdk


@dataclass(frozen=True)
class TextToSpeechWord:
    """
    This class encapsulates a word in the output of a text-to-speech conversion. It includes the word itself, the timestamp when the word was spoken, its index in the text, and its category (e.g., word, punctuation), using Azure's Speech Synthesis Boundary Type.

    The purpose of this class is to provide a structured representation of a word in the output of a text-to-speech
    conversion, allowing for easy access to its properties and enabling further processing or analysis of the spoken
    text.

    Attributes:
        word (str): The word that has been converted to speech.
        timestamp (datetime.datetime): The datetime when the word was spoken.
        word_index (int): The position of the word in the original text.
        category (speechsdk.SpeechSynthesisBoundaryType): The category of the word (e.g., word, punctuation).
    """

    word: str
    timestamp: datetime.datetime
    word_index: int
    category: speechsdk.SpeechSynthesisBoundaryType

    def __len__(self) -> int:
        """
        Computes and returns the length of the word.

        This method is useful for determining the length of the word without having to access the `word` attribute
        directly. It can be used, for example, in filtering or sorting operations on a list of `TextToSpeechWord`
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
            str: A string containing the word and its timestamp in ISO 8601 format.
        """
        description = f"<TextToSpeechWord '{self.word}' at {self.timestamp}>"
        return description

    def __repr__(self) -> str:
        """
        Returns the word itself as its string representation. This simplifies the display of the object in certain
        contexts, such as when printing a list of `TextToSpeechWord` instances.

        This method is called by built-in Python functions like `repr()` and is used, for example, when displaying the
        object in an interactive Python session or when printing a list containing the object.

        Returns:
            str: The word itself.
        """
        return self.word
