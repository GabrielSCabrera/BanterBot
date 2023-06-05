import datetime
import json
from typing import Iterator, List, TypedDict

import azure.cognitiveservices.speech as speechsdk
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.enums import SpeechProcessingType, WordCategory
from banterbot.utils.nlp import NLP
from banterbot.utils.word import Word


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


class SpeechToTextOutput:
    """
    A class that encapsulates the speech-to-text output data.

    Attributes:
        recognition_result (speechsdk.SpeechRecognitionResult): The speech recognition result.
    """

    def __init__(self, recognition_result: speechsdk.SpeechRecognitionResult) -> None:
        """
        Constructor for the SpeechToTextOutput class. Designed to create lightweight instances with most attributes
        initially set to None. Computation-intensive operations are performed on-demand when respective properties are
        accessed, instead of during initialization.

        Args:
            recognition_result (speechsdk.SpeechRecognitionResult): The result from a speech recognition event.
        """
        self._data = json.loads(recognition_result.json)
        self._offset = None
        self._duration = None
        self._sents = None
        self._words = None

    def _extract_words(self, words_raw: List[WordJSON]) -> List[Word]:
        """
        Private method that extracts Word objects from raw data.

        Args:
            words_raw (List[WordJSON]): A list of dictionaries containing raw data of words.

        Returns:
            List[Word]: A list of Word objects.
        """
        words = []
        for word in words_raw:
            words.append(
                Word(
                    word=word["Word"],
                    offset=datetime.timedelta(microseconds=word["Offset"] / 10),
                    duration=datetime.timedelta(microseconds=word["Duration"] / 10),
                    category=WordCategory.WORD,
                    source=SpeechProcessingType.STT,
                    confidence=word["Confidence"],
                )
            )
        return words

    @property
    def words(self) -> List[Word]:
        """
        A getter property that returns a list of Word objects. If the list is not already computed, it triggers
        computation.

        Returns:
            List[str]: A list of sentences.

        """
        if self._words is None:
            self._words = self._extract_words(words_raw=self._data["NBest"][0].words)
        return self._words

    @property
    def sents(self) -> List[str]:
        """
        A getter property that returns a list of sentences. If the list is not already computed, it triggers
        computation.

        Returns:
            List[str]: A list of sentences.
        """
        if self._sents is None:
            self._sents = NLP.segment_sentences(string=self._data["NBest"][0]["Display"], whitespace=True)
        return self._sents

    @property
    def recognition_status(self) -> str:
        """
        A getter property that returns the recognition status.

        Returns:
            str: The recognition status.
        """
        return self._data["RecognitionStatus"]

    @property
    def offset(self) -> datetime.timedelta:
        """
        A getter property that returns the offset of the recognized speech in the audio stream.

        Returns:
            datetime.timedelta: The offset in the form of a datetime.timedelta object.
        """
        if self._offset is None:
            self._offset = datetime.timedelta(microseconds=self._data["Offset"] / 10)
        return self._offset

    @property
    def duration(self) -> datetime.timedelta:
        """
        A getter property that returns the duration of the recognized speech in the audio stream.

        Returns:
            datetime.timedelta: The duration in the form of a datetime.timedelta object.
        """
        if self._duration is None:
            self._duration = datetime.timedelta(microseconds=self._data["Duration"] / 10)
        return self._duration

    @property
    def confidence(self) -> float:
        """
        A getter property that returns the confidence score of the recognized speech.

        Returns:
            float: The confidence score.
        """
        return self._data["NBest"][0]["Confidence"]

    @property
    def lexical(self) -> str:
        """
        A getter property that returns the lexical form of the recognized speech.

        Returns:
            str: The lexical form of the speech.
        """
        return self._data["NBest"][0]["Lexical"]

    @property
    def ITN(self) -> str:
        """
        A getter property that returns the ITN (Inverse Text Normalization) form of the recognized speech.

        Returns:
            str: The ITN form of the speech.
        """
        return self._data["NBest"][0]["ITN"]

    @property
    def maskedITN(self) -> str:
        """
        A getter property that returns the masked ITN (Inverse Text Normalization) form of the recognized speech.

        Returns:
            str: The masked ITN form of the speech.
        """
        return self._data["NBest"][0]["MaskedITN"]

    @property
    def display(self) -> str:
        """
        A getter property that returns the display form of the recognized speech. The display form is fully processed
        with Inverse Text Normalization (ITN), Capitalization, Disfluency Removal, and Punctuation.

        Returns:
            str: The display form of the speech.
        """
        return self._data["NBest"][0]["Display"]

    def __getitem__(self, idx: int) -> Word:
        """
        Overloads the indexing operator to retrieve words at specific positions.

        Args:
            idx (int): The index of the word to retrieve.

        Returns:
            Word: The word at the specified index.
        """
        return self.words[idx]

    def __iter__(self) -> Iterator[Word]:
        """
        Overloads the iterator to allow for iteration over the Word objects in the output.

        Yields:
            Word: The next Word object in the output.
        """
        for word in self.words:
            yield word

    def __len__(self) -> int:
        """
        Overloads the len() operator to return the number of words in the output.

        Returns:
            int: The number of words in the output.
        """
        return len(self.words)

    def __str__(self) -> str:
        """
        Overloads the str() operator to return the fully processed speech-to-text output. The processing includes
        Inverse Text Normalization (ITN), Capitalization, Disfluency Removal, and Punctuation.

        Returns:
            str: The fully processed string representation of the speech-to-text output.
        """
        return self.display
