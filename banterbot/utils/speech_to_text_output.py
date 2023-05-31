import json
from typing import Iterator, List

import azure.cognitiveservices.speech as speechsdk

from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.utils.word import Word


class SpeechToTextOutput:
    def __init__(self, recognition_result: speechsdk.SpeechRecognitionResult) -> None:

        self._data = json.loads(recognition_result.json)

        self.words: List[Word] = self._data["NBest"]

    @property
    def recognition_status(self):
        return self._data["RecognitionStatus"]

    @property
    def offset(self):
        return self._data["Offset"]

    @property
    def duration(self):
        return self._data["Duration"]

    @property
    def confidence(self):
        return self._data["NBest"][0]["Confidence"]

    @property
    def lexical(self):
        return self._data["NBest"][0]["Lexical"]

    @property
    def ITN(self):
        return self._data["NBest"][0]["ITN"]

    @property
    def maskedITN(self):
        return self._data["NBest"][0]["MaskedITN"]

    @property
    def display(self):
        return self._data["NBest"][0]["Display"]

    def __getitem__(self, idx: int) -> Word:
        """
        Allows for indexing into the SpeechToTextOutput object to retrieve words at specific positions.

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
        Allows for the use of len() on a SpeechToTextOutput instance, returning the number of words in the output.

        Returns:
            int: The number of words in the output.
        """
        return len(self.words)

    def __str__(self) -> str:
        """
        Converts the SpeechToTextOutput instance into a string, concatenating all the words in the output.

        Returns:
            str: The string representation of the speech-to-text output. This will be a concatenation of all the words
            in the output, in the order they appear in the words list.
        """
        return "".join(word.word for word in self.words)
