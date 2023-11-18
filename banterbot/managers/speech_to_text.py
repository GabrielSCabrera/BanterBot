import datetime
import logging
import os
import threading
import time
from typing import Generator, Optional, Union

import azure.cognitiveservices.speech as speechsdk

from banterbot.config import DEFAULT_LANGUAGE, soft_interruption_delay
from banterbot.data.enums import EnvVar
from banterbot.utils.speech_to_text_output import SpeechToTextOutput


class SpeechToText:
    """
    The SpeechToText class provides an interface to convert spoken language into written text using Azure Cognitive
    Services. It allows continuous speech recognition and provides real-time results as sentences are recognized.
    """

    # Create a lock that prevents race conditions when listening
    _listen_lock = threading.Lock()

    def __init__(
        self,
        languages: Union[str, list[str]] = None,
        phrase_list: Optional[list[str]] = None,
    ) -> None:
        """
        Initializes the SpeechToText instance by setting up the Azure Cognitive Services speech configuration and
        recognizer. Argument `recognition_language` can take one or more values, each representing a language the
        recognizer can expect to receive as an input. The recognizer will attempt to auto-detect the language if
        multiple are provided.

        Args:
            languages (Union[str, list[str]): The language(s) the speech-to-text recognizer expects to hear.
            phrase_list(list[str], optional): Optionally provide the recognizer with context to improve recognition.
        """
        logging.debug(f"SpeechToText initialized")

        # Initialize the speech configuration with the Azure subscription and region
        self._speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get(EnvVar.AZURE_SPEECH_KEY.value),
            region=os.environ.get(EnvVar.AZURE_SPEECH_REGION.value),
        )

        # Allowing the speech configuration to recognize profane words
        self._speech_config.set_profanity(speechsdk.ProfanityOption.Raw)

        # Activate the receipt of data pertaining to word timings
        self._speech_config.request_word_level_timestamps()

        # Initialize the output and total length variables
        self._outputs: list[SpeechToTextOutput] = []

        # Determine whether language auto-detection should be activated
        self._languages = DEFAULT_LANGUAGE if languages is None else languages
        self._auto_detection = not isinstance(self._languages, str)

        # Initialize the speech recognizer with the speech configuration and language settings
        self._recognizer = speechsdk.SpeechRecognizer(speech_config=self._speech_config, **self._language_kwargs())

        # Initialize an instance of `PhraseListGrammar` which is used to provide context to improve speech recognition
        self._phrase_list_grammar = speechsdk.PhraseListGrammar.from_recognizer(self._recognizer)

        # Connect the speech recognizer events to their corresponding callbacks
        self._recognizer_events_connect()

        # Creating a new instance of Connection class
        self._connection = speechsdk.Connection.from_recognizer(self._recognizer)

        # Pre-connecting the speech recognizer for reduced latency
        self._connection.open(True)

        # Set the interruption flag to zero: if interruptions are raised, this will be updated
        self._interrupt: int = 0

        # Initialize events.
        self._start_recognition: threading.Event = threading.Event()
        self._stop_recognition: threading.Event = threading.Event()
        self._new_events: threading.Event = threading.Event()

        # Set the total offset to zero, which will increment as recognitions occur.
        self._total_offset = datetime.timedelta(seconds=0)
        self._last_total_offset = 0

        # Reset the state variables of the speech-to-text recognizer
        self._reset()

    def interrupt(self, soft: bool = False, shutdown_time: Optional[int] = None) -> None:
        """
        Interrupts an ongoing speech-to-text process, if any. This method sets the interrupt flag to the current time,
        which will stop any speech-to-text processes activated prior to the current time.

        Args:
            soft (bool): If True, allows the recognizer to keep processing data that was recorded prior to interruption.
            shutdown_time (Optional[int]): The time at which the listener was deactivated.
        """
        # Allow the recognizer to wait for any buffering words to be completely recognized.
        self._soft_interrupt = shutdown_time if soft else self._soft_interrupt
        # Update the interruption time.
        self._interrupt: int = shutdown_time if shutdown_time is not None else time.perf_counter_ns()
        # Release any threading.Event instances that the listener may be waiting for.
        self._start_recognition.set()
        self._new_events.set()
        # If a hard interrupt is initiated, interrupt the Event waiting for the recognition to end.
        if not soft:
            self._stop_recognition.set()
        logging.debug("SpeechToText listener interrupted")

    def listen(self, init_time: Optional[int] = None) -> Generator[str, None, None]:
        """
        Starts the speech-to-text recognition process and yields sentences as they are recognized.

        Yields:
            Generator[str, None, None]: A generator that yields tuples of recognized sentences.
            init_time (Optional[int]): The time at which the listener was activated.
        """
        # Record the time at which the thread was initialized pre-lock, in order to account for future interruptions.
        init_time = init_time if init_time is not None else time.perf_counter_ns()

        # Only allow one listener to be active at once.
        with self.__class__._listen_lock:

            # Do not run the listener if an interruption was raised after `init_time`.
            if self._interrupt <= init_time:

                # Prepare a list which will contain all the recognized input words.
                output = []
                self._outputs.append(output)

                # Set the listening flag to True
                self._listening = True

                # Monitor the recognition progress in the main thread, yielding sentences as they are processed
                for block in self._callbacks_process(output=output, init_time=init_time):
                    logging.debug(f"SpeechToText listener processed block: `{block}`")
                    yield block

                logging.debug("SpeechToText listener stopped")

                # Reset all state attributes
                self._reset()

    @property
    def listening(self) -> bool:
        """
        If the current instance of SpeechToText is in the process of listening, returns True. Otherwise, returns False.

        Returns:
            bool: The listening state of the current instance.
        """
        return self._listening

    @property
    def languages(self) -> str:
        """
        Returns the language(s) being recognized by the Speech-to-Text recognizer.

        Returns:
            list[str]: The language-country pairs being used by the recognizer.
        """
        return self._languages

    def add_phrases(self, phrases: list[str]) -> None:
        """
        Add a new phrase to the PhraseListGrammar instance, which implements a bias towards the given words/phrases that
        can help improve speech recognition in circumstances where there may be potential ambiguity.

        Args:
            phrases(list[str]): Provide the recognizer with additional text context to improve recognition.
        """
        for phrase in phrases:
            self._phrase_list_grammar.addPhrase(phrase)

    def clear_phrases(self) -> None:
        """
        Clear all phrases from the PhraseListGrammar instance.
        """
        self._phrase_list_grammar.clear()

    def _language_kwargs(self) -> dict:
        """
        Set the language(s) being recognized by the Speech-to-Text recognizer in two modes: if a string is given to
        argument `languages` in the __init__ method, then set the language explicitly in the Azure speech SDK
        `SpeechRecognizer` object in this `SpeechToText` instance. If a list of languages is given, use the
        `AutoDetectSourceLanguageConfig` object from the speech SDK to allow the `SpeechRecognizer` to automatically
        choose the input language from one of those provided.

        Returns:
            dict: A dictionary of keywords arguments for the Speech Recognizer.
        """
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

    def _reset(self) -> None:
        """
        Resets the state variables of the speech-to-text recognizer, such as the list of events, the listening flag,
        the soft interruption flag, recognition started flag, recognition stopped flag, and new events flag.
        """
        self._events: list[SpeechToTextOutput] = []
        self._listening: bool = False
        self._soft_interrupt: bool = False
        self._start_recognition_time = 0
        self._start_recognition.clear()
        self._stop_recognition.clear()
        self._new_events.clear()

    def _recognizer_events_connect(self) -> None:
        """
        Connects the speech-to-text recognizer events to their corresponding callbacks.
        """
        # Connect the session_started event to the `_callback_started` method
        self._recognizer.session_started.connect(self._callback_started)

        # Connect the recognized event to the `_process_recognized` method
        self._recognizer.recognized.connect(self._process_recognized)

        # Connect the recognized event to the `_callback_ended` method
        self._recognizer.session_stopped.connect(self._callback_ended)

    def _callback_ended(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Detects when the speech recognizer has disconnected, triggering a `threading.Event` instance.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the recognition stopped.
        """
        logging.debug("Recognizer disconnected")
        self._stop_recognition.set()

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for recognition started event. Signals that the recognition process has started.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the recognition started.
        """
        logging.debug("Recognizer connected")
        self._start_recognition_time = time.perf_counter_ns()
        self._start_recognition.set()

    def _callbacks_process(self, output: list[SpeechToTextOutput], init_time: int) -> Generator[str, None, None]:
        """
        Processes the recognized speech events and appends them to the output list. Yields sentences as they are
        processed.

        Args:
            output (list[SpeechToTextOutput]): The list in which to store the recognized speech events.
            init_time (int): The time at which the listening was initialized.

        Yields:
            Generator[str, None, None]: A generator that yields sentences as they are processed.
        """
        # Initialize variables
        idx = 0

        # Starting the speech recognizer
        self._recognizer.start_continuous_recognition()

        # Wait until the recognition has started before proceeding
        self._start_recognition.wait()

        t = time.perf_counter_ns()
        logging.debug("SpeechToText listener started")

        # Continuously monitor the recognition progress
        while self._interrupt <= init_time:

            self._new_events.wait()
            self._new_events.clear()

            while self._interrupt <= init_time and idx < len(self._events):
                output.append(self._events[idx])
                yield str(self._events[idx])
                idx += 1

        dt = self._start_recognition_time + 1e3 * soft_interruption_delay.microseconds + self._interrupt - init_time

        # Stop the recognizer
        self._recognizer.stop_continuous_recognition()

        if self._soft_interrupt >= self._interrupt:
            # Prepare a timedelta object indicating how long the listener was active.
            cutoff = datetime.timedelta(microseconds=1e-3 * (self._interrupt - init_time)) + soft_interruption_delay
            for idx in range(idx, len(self._events)):

                if self._events[idx].offset - self._total_offset > cutoff:
                    break
                elif self._events[idx].offset_end - self._total_offset > cutoff:
                    if (event := self._events[idx].from_cutoff(upper_cutoff=cutoff)) is not None:
                        self._events[idx] = event

                output.append(self._events[idx])
                yield str(self._events[idx])
                idx += 1

    def _process_recognized(self, event: speechsdk.SpeechRecognitionEventArgs) -> None:
        """
        Processes the recognized speech event by appending it to the list of events and setting the `new_events` flag.

        Args:
            event (speechsdk.SpeechRecognitionEventArgs): The recognized speech event.
        """
        if self._start_recognition_time > self._last_total_offset:
            self._last_total_offset = self._start_recognition_time
            self._total_offset = datetime.timedelta(microseconds=event.offset / 10)

        self._events.append(
            SpeechToTextOutput.from_recognition_result(
                event.result, self._languages if not self._auto_detection else None
            )
        )
        self._new_events.set()
