from typing import TypedDict


class WordJSON(TypedDict):
    """
    A type definition class defining the format of the individually recognized words from a SpeechRecognitionEventArgs
    event's json attribute.

    Attributes:
        Word (str): The recognized word from speech.
        Offset (int): The start time of the recognized word in microseconds.
        Duration (int): The length of time the recognized word took in microseconds.
        Confidence (float): Confidence score of the recognition for the word.
    """

    Word: str
    Offset: int
    Duration: int
    Confidence: float
