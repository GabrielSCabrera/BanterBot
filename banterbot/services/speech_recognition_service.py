import datetime
import logging
import os
import threading
import time
from typing import Optional, Union

import azure.cognitiveservices.speech as speechsdk

from banterbot.config import DEFAULT_LANGUAGE, INTERRUPTION_DELAY
from banterbot.data.enums import EnvVar
from banterbot.handlers.speech_recognition_handler import SpeechRecognitionHandler
from banterbot.handlers.stream_handler import StreamHandler
from banterbot.managers.stream_manager import StreamManager
from banterbot.models.speech_recognition_input import SpeechRecognitionInput
from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.utils.closeable_queue import CloseableQueue


class SpeechRecognitionService:
    """
    The `SpeechRecognitionService` class provides an interface to convert spoken language into written text using Azure
    Cognitive Speech Services. It allows continuous speech recognition and provides real-time results as sentences are
    recognized.
    """

    # Create a lock that prevents race conditions when recognizing speech
    _recognition_lock = threading.Lock()

    def __init__(
        self,
        languages: Union[str, list[str]] = None,
        phrase_list: Optional[list[str]] = None,
    ) -> None:
        """
        Initializes the `SpeechRecognitionService` instance by setting up the Azure Cognitive Services speech
        configuration and recognizer. Argument `recognition_language` can take one or more values, each representing a
        language the recognizer can expect to receive as an input. The recognizer will attempt to auto-detect the
        language if multiple are provided.

        Args:
            languages (Union[str, list[str]): The language(s) the speech-to-text recognizer expects to hear.
            phrase_list(list[str], optional): Optionally provide the recognizer with context to improve recognition.
        """
        # Initialize the `SpeechRecognizer`.
        self._init_recognizer(languages=languages, phrase_list=phrase_list)

        # Set the total offset to zero, which will increment as recognitions occur.
        self._total_offset = datetime.timedelta(seconds=0)
        self._last_total_offset = 0

        # Initialize the `StreamManager` for handling streaming processes.
        self._stream_manager = StreamManager()

        # The latest interruption time.
        self._interrupt = 0

        # A list of active stream handlers.
        self._stream_handlers = []
        self._stream_handlers_lock = threading.Lock()

    def interrupt(self, kill: bool = False) -> None:
        """
        Interrupts the current speech recognition process.

        Args:
            kill (bool): Whether the interruption should kill the queues or not.
        """
        self._interrupt = time.perf_counter_ns()
        with self._stream_handlers_lock:
            for handler in self._stream_handlers:
                handler.interrupt(kill=kill)
            self._stream_handlers.clear()
        logging.debug(f"SpeechRecognitionService Interrupted")

    def phrases_add(self, phrases: list[str]) -> None:
        """
        Add a new phrase to the PhraseListGrammar instance, which implements a bias towards the specified words/phrases
        that can help improve speech recognition in circumstances where there may be potential ambiguity.

        Args:
            phrases(list[str]): Provide the recognizer with additional text context to improve recognition.
        """
        for phrase in phrases:
            self._phrase_list_grammar.addPhrase(phrase)

    def phrases_clear(self) -> None:
        """
        Clear all phrases from the PhraseListGrammar instance.
        """
        self._phrase_list_grammar.clear()

    def recognize(self, init_time: Optional[int] = None) -> Union[StreamHandler, tuple[()]]:
        """
        Recognizes speech and returns a generator that yields the recognized sentences as they are processed.

        Args:
            init_time (Optional[int]): The time at which the recognition was initialized.

        Returns:
            Union[StreamHandler, tuple[()]: A handler for the stream of recognized sentences, or an empty tuple if the
                recognition was interrupted.
        """
        # Record the time at which the recognition was initialized pre-lock, in order to account for future interruptions.
        init_time = time.perf_counter_ns() if init_time is None else init_time

        # Only allow one listener to be active at once.
        with self.__class__._recognition_lock:
            if self._interrupt >= init_time:
                return tuple()
            else:
                self._queue = CloseableQueue()

                iterable = SpeechRecognitionHandler(recognizer=self._recognizer, queue=self._queue)
                handler = self._stream_manager.stream(
                    iterable=iterable, close_stream=iterable.close, init_shared_data={"init_time": init_time}
                )
                with self._stream_handlers_lock:
                    self._stream_handlers.append(handler)
                return handler

    def _init_recognizer(
        self, languages: Union[str, list[str]] = None, phrase_list: Optional[list[str]] = None
    ) -> None:
        """
        Initialize an instance of the the Microsoft Azure Cognitive Services Speech SDK `SpeechRecognizer` class and
        configure it with any user-provided custom settings, or alternatively its package defaults, then open a
        connection to reduce overhead.

        Args:
            languages (Union[str, list[str]): The language(s) the speech-to-text recognizer expects to hear.
            phrase_list(list[str], optional): Optionally provide the recognizer with context to improve recognition.
        """
        logging.debug(f"SpeechRecognitionService initialized")

        # Initialize the speech configuration with the Azure subscription and region
        self._speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get(EnvVar.AZURE_SPEECH_KEY.value),
            region=os.environ.get(EnvVar.AZURE_SPEECH_REGION.value),
        )

        # Allowing the speech configuration to recognize profane words
        self._speech_config.set_profanity(speechsdk.ProfanityOption.Raw)

        # Activate the receipt of data pertaining to word timings
        self._speech_config.request_word_level_timestamps()

        # Initialize the speech recognizer with the speech configuration and language settings
        self._recognizer = speechsdk.SpeechRecognizer(
            speech_config=self._speech_config, **self._language_kwargs(languages=languages)
        )

        # Initialize an instance of `PhraseListGrammar` which is used to provide context to improve speech recognition
        self._phrase_list_grammar = speechsdk.PhraseListGrammar.from_recognizer(self._recognizer)

        # Add any phrases in `phrase_list` to the `PhraseListGrammar`.
        if phrase_list:
            self.phrases_add(phrase_list)

        # Connect the speech recognizer events to their corresponding callbacks
        self._callbacks_connect()

        # Creating a new instance of Connection class
        self._connection = speechsdk.Connection.from_recognizer(self._recognizer)

        # Pre-connecting the speech recognizer for reduced latency
        self._connection.open(True)

    def _language_kwargs(self, languages: Union[str, list[str]] = None) -> dict:
        """
        Set the language(s) being recognized by the Speech-to-Text recognizer in two modes: if a string is given to
        argument `languages` in the __init__ method, then set the language explicitly in the Azure speech SDK
        `SpeechRecognizer` object in this `SpeechRecognitionService` instance. If a list of languages is given, use the
        `AutoDetectSourceLanguageConfig` object from the speech SDK to allow the `SpeechRecognizer` to automatically
        choose the input language from one of those provided.

        Args:
            languages (Union[str, list[str]): The language(s) the speech-to-text recognizer expects to hear.

        Returns:
            dict: A dictionary of keywords arguments for the Speech Recognizer.
        """
        # Determine whether language auto-detection should be activated
        self._languages = DEFAULT_LANGUAGE if languages is None else languages
        self._auto_detection = not isinstance(self._languages, str)

        if self._auto_detection:
            self._speech_config.set_property(
                property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode,
                value="Continuous",
            )
            config = speechsdk.AutoDetectSourceLanguageConfig(languages=self._languages)
            kwargs = {"auto_detect_source_language_config": config}
        else:
            config = speechsdk.SourceLanguageConfig(language=self._languages)
            kwargs = {"source_language_config": config}

        return kwargs

    def _callback_completed(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Detects when the speech recognizer has disconnected, triggering a `threading.Event` instance.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the recognition stopped.
        """
        logging.debug("SpeechRecognitionService disconnected")
        self._queue.close()

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for recognition started event. Signals that the recognition process has started.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the recognition started.
        """
        logging.debug("SpeechRecognitionService connected")
        self._start_recognition_time = time.perf_counter_ns()

    def exception_handler(self, log: list[StreamLogEntry], index: int, shared_data: dict):
        """
        Handles exceptions that occur during the processing of the stream log.
        """
        cutoff = (
            datetime.timedelta(microseconds=1e-3 * (shared_data["interrupt"] - shared_data["init_time"]))
            + INTERRUPTION_DELAY
        )
        if log[index].offset - self._total_offset > cutoff:
            raise StopIteration
        elif log[index].offset_end - self._total_offset > cutoff:
            if (event := log[index].from_cutoff(upper_cutoff=cutoff)) is not None:
                log[index] = event

        return log[index]

    def _callback_recognized(self, event: speechsdk.SpeechRecognitionEventArgs) -> None:
        """
        Processes the recognized speech event by appending it to the list of events and setting the `new_events` flag.

        Args:
            event (speechsdk.SpeechRecognitionEventArgs): The recognized speech event.
        """
        if self._start_recognition_time > self._last_total_offset:
            self._last_total_offset = self._start_recognition_time
            self._total_offset = datetime.timedelta(microseconds=event.offset / 10)

        self._queue.put(
            SpeechRecognitionInput.from_recognition_result(
                event.result, self._languages if not self._auto_detection else None
            )
        )

    def _callbacks_connect(self) -> None:
        """
        Connects the recognizer events to their corresponding callback methods.
        """
        self._recognizer.session_started.connect(self._callback_started)
        self._recognizer.recognized.connect(self._callback_recognized)
        self._recognizer.canceled.connect(self._callback_completed)
        self._recognizer.session_stopped.connect(self._callback_completed)
