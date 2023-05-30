import datetime
from typing import Iterator, List

from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.utils.word import Word


class TextToSpeechOutput:
    """
    The TextToSpeechOutput class encapsulates the output of a text-to-speech conversion, providing a convenient
    interface for working with and manipulating the converted data. This class is designed to store the input text, the
    timestamp, the voice and style used for conversion, and the list of Word objects representing the individual words
    in the output.

    The primary use case for this class is to store the output of a text-to-speech conversion and provide an easy way to
    access the words in the output. This can be useful for applications that require further processing or analysis of
    the converted text, such as natural language processing or speech synthesis.
    """

    def __init__(self, input_string: str, timestamp: datetime.datetime, voice: AzureNeuralVoice, style: str) -> None:
        """
        Initializes a new TextToSpeechOutput instance, setting up the input string and preparing the words list for the
        converted words.

        Args:
            input_string (str): The input string that is to be converted into speech.

            timestamp (datetime.datetime): The time at which the speech began.

            voice (AzureNeuralVoice): The voice to be used for the text-to-speech conversion. This should be an instance
            of the AzureNeuralVoice class, which represents a specific voice available in the Azure Cognitive Services
            Text-to-Speech API.

            style (str): The speaking style to be applied to the text-to-speech conversion. This should be a string
            representing one of the available speaking styles in the Azure Cognitive Services Text-to-Speech API, such
            as "cheerful", "sad", or "angry".
        """
        self.input_string = input_string
        self.timestamp = timestamp
        self.voice = voice
        self.style = style

        self.words: List[Word] = []

    def __getitem__(self, idx: int) -> Word:
        """
        Allows for indexing into the TextToSpeechOutput object to retrieve words at specific positions.

        Args:
            idx (int): The index of the word to retrieve.

        Returns:
            Word: The word at the specified index.
        """
        return self.words[idx]

    def __iter__(self) -> Iterator[Word]:
        """
        Provides an iterator to iterate over the Word objects in the output.

        Yields:
            Word: The next Word object in the output.
        """
        for word in self.words:
            yield word

    def __len__(self) -> int:
        """
        Allows for the use of len() on a TextToSpeechOutput instance, returning the number of words in the output.

        Returns:
            int: The number of words in the output.
        """
        return len(self.words)

    def __str__(self) -> str:
        """
        Converts the TextToSpeechOutput instance into a string, concatenating all the words in the output.

        Returns:
            str: The string representation of the text-to-speech output. This will be a concatenation of all the words
            in the output, in the order they appear in the words list.
        """
        return "".join(word.word for word in self.words)

    def append(self, entry: Word) -> None:
        """
        Appends a Word object to the words list in the output.

        Args:
            entry (Word): The word to be appended to the output. This should be an instance of the Word class, which
            represents a single word in the text-to-speech output along with its associated metadata.
        """
        self.words.append(entry)
