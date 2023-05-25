import datetime
from dataclasses import dataclass

import azure.cognitiveservices.speech as speechsdk


@dataclass(frozen=True)
class TextToSpeechWord:
    """
    Represents a word in the text-to-speech output.
    """

    # The word itself
    word: str
    # The timestamp when the word was spoken
    timestamp: datetime.datetime
    # The index of the word in the text
    word_index: int
    # The category of the word (e.g., word, punctuation)
    category: speechsdk.SpeechSynthesisBoundaryType

    def __len__(self) -> int:
        """
        Returns the length of the word.

        Returns:
            The length of the word as an integer.
        """
        return len(self.word)

    def __str__(self) -> str:
        """
        Returns a string representation of the instance attributes.

        Returns:
            The word as a string.
        """
        description = f"<TextToSpeechWord '{self.word}' at {self.timestamp.isoformat()}>"
        return description

    def __repr__(self) -> str:
        """
        Returns a string representation of the word.

        Returns:
            The word as a string.
        """
        return self.word
