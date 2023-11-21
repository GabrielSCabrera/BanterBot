import datetime
import json
from typing import Iterator, Optional

import azure.cognitiveservices.speech as speechsdk
from typing_extensions import Self

from banterbot.data.enums import SpaCyLangModel, SpeechProcessingType, WordCategory
from banterbot.models.word import Word
from banterbot.types.wordjson import WordJSON
from banterbot.utils.nlp import NLP


class SpeechRecognitionOutput:
    """
    A class that encapsulates the speech-to-text output data.
    """

    @classmethod
    def from_recognition_result(
        cls, recognition_result: speechsdk.SpeechRecognitionResult, language: Optional[str] = None
    ) -> Self:
        """
        Constructor for the `SpeechRecognitionOutput` class. Designed to create lightweight instances with most
        attributes initially set to None. Computation-intensive operations are performed on-demand when respective
        properties are accessed, instead of during initialization.

        Args:
            recognition_result (speechsdk.SpeechRecognitionResult): The result from a speech recognition event.
            language (str, optional): The language used during the speech-to-text recognition, if not auto-detected.
        """
        data = json.loads(recognition_result.json)
        language = language if language is not None else self._extract_language(recognition_result=recognition_result)
        return cls(data=data, language=language)

    @classmethod
    def _extract_language(cls, recognition_result: speechsdk.SpeechRecognitionResult) -> Optional[str]:
        """
        If the language is not provided (as it should be if auto-detection is disabled) then extract the auto-detected
        language as a string. Return None if the process fails.

        Args:
            recognition_result (speechsdk.SpeechRecognitionResult): The result from a speech recognition event.

        Returns:
            str, optional: The auto-detected language from the speech-to-text output.
        """
        language_key = speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
        language = None
        if language_key in recognition_result.properties:
            language = recognition_result.properties[language_key]
        return language

    def __init__(
        self,
        data: dict,
        language: str,
        offset: Optional[datetime.timedelta] = None,
        duration: Optional[datetime.timedelta] = None,
        offset_end: Optional[datetime.timedelta] = None,
        sents: Optional[tuple[str, ...]] = None,
        words: Optional[list[Word]] = None,
    ) -> None:
        """
        Constructor for the `SpeechRecognitionOutput` class. Designed to create lightweight instances with most
        attributes initially set to None unless provided explicitly on initialization. Computation-intensive operations
        are instead performed lazily: i.e., when respective properties are accessed.

        Args:
            data (speechsdk.SpeechRecognitionResult): The JSON data output from a speech recognition event.
            language (str): The language used during the speech-to-text recognition.
            offset (optional, datetime.timedelta): The number of milliseconds between recognition start and the output.
            duration (optional, datetime.timedelta): The duration of the output in milliseconds.
            sents (optional, tuple[str, ...]): The split sentences of the output as a tuple.
            words (optional, list[Word]): A list of words from the output.

        """
        self._data = data
        self._language = language
        self._offset = offset
        self._duration = duration
        self._offset_end = offset_end
        self._sents = sents
        self._words = words

    def from_cutoff(
        self, lower_cutoff: Optional[datetime.timedelta] = None, upper_cutoff: Optional[datetime.timedelta] = None
    ) -> Self:
        """
        Create a new instance of class `SpeechRecognitionOutput` that only contains the text spoken within a cutoff
        interval.

        Args:
            lower_cutoff (datetime.timedelta): The lower cutoff time (or duration) of the new instance.
            upper_cutoff (datetime.timedelta): The upper cutoff time (or duration) of the new instance.

        Returns:
            SpeechRecognitionOutput: The new instance of `SpeechRecognitionOutput`.
        """

        doc = NLP.model(SpaCyLangModel.EN_CORE_WEB_SM)(self.display)

        words = []
        last_token_end = 0

        for token in doc:
            for word in self.words:
                if (
                    token.text.lower() == word.word
                    and (upper_cutoff is None or word.offset <= upper_cutoff)
                    and (lower_cutoff is None or word.offset >= lower_cutoff)
                ):
                    words.append(word)
                    last_token_end = token.idx + len(token.text)
                    break

        if len(words) > 0:
            data = {
                "Id": self._data["Id"],
                "RecognitionStatus": self._data["RecognitionStatus"],
                "Offset": self._data["Offset"],
                "Duration": sum(i["Duration"] for i in self._data["NBest"][0]["Words"][: len(words)]),
                "Channel": self._data["Channel"],
                "DisplayText": self.display[:last_token_end],
                "NBest": [
                    {
                        "Confidence": self._data["NBest"][0]["Confidence"],
                        "Lexical": self._data["NBest"][0]["Lexical"],
                        "ITN": self._data["NBest"][0]["ITN"],
                        "MaskedITN": self._data["NBest"][0]["MaskedITN"],
                        "Display": self._data["NBest"][0]["Display"],
                        "Words": self._data["NBest"][0]["Words"][: len(words)],
                    }
                ],
            }

            return self.__class__(data=data, language=self._language)

        else:
            return None

    def _extract_words(self, words_raw: list[WordJSON]) -> list[Word]:
        """
        Private method that extracts `Word` objects from raw data.

        Args:
            words_raw (list[WordJSON]): A list of dictionaries containing raw word data.

        Returns:
            list[Word]: A list of `Word` objects.
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
    def words(self) -> list[Word]:
        """
        A getter property that returns a list of Word objects. If the list is not already computed, it triggers
        computation.

        Returns:
            list[str]: A list of words.
        """
        if self._words is None:
            self._words = self._extract_words(words_raw=self._data["NBest"][0]["Words"])
        return self._words

    @property
    def sents(self) -> tuple[str, ...]:
        """
        A getter property that returns a list of sentences. If the list is not already computed, it triggers
        computation.

        Returns:
            list[str]: A list of sentences.
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
    def offset_end(self) -> datetime.timedelta:
        """
        A getter property that returns the offset + duration of the recognized speech in the audio stream.

        Returns:
            datetime.timedelta: The duration + offset in the form of a datetime.timedelta object.
        """
        if self._offset_end is None:
            self._offset_end = self.offset + self.duration
        return self._offset_end

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
        Overloads the iterator to allow for iteration over the `Word` objects in the output.

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
