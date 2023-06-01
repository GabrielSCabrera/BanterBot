import os
import threading
from typing import Generator, List, Tuple

import azure.cognitiveservices.speech as speechsdk

from banterbot.data.enums import EnvVar
from banterbot.utils.speech_to_text_output import SpeechToTextOutput
from banterbot.utils.word import Word


class SpeechToText:
    """
    The SpeechToText class provides an interface to convert spoken language into written text using Azure Cognitive
    Services. It allows continuous speech recognition and provides real-time results as sentences are recognized.
    """

    # Create a lock that prevents race conditions when listening
    _listen_lock = threading.Lock()

    def __init__(self) -> None:
        """
        Initializes the SpeechToText instance by setting up the Azure Cognitive Services speech configuration and
        recognizer.
        """

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
        self._outputs: List[SpeechToTextOutput] = []

        # Initialize the speech recognizer with the speech configuration
        self._recognizer = speechsdk.SpeechRecognizer(speech_config=self._speech_config)

        # Connect the speech recognizer events to their corresponding callbacks
        self._recognizer_events_connect()

        # Creating a new instance of Connection class
        self._connection = speechsdk.Connection.from_recognizer(self._recognizer)

        # Preconnecting the speech recognizer for reduced latency
        self._connection.open(True)

        # Reset the state variables of the speech-to-text recognizer
        self._reset()

    def interrupt(self) -> None:
        """
        Interrupts an ongoing speech-to-text process, if any. This method sets the interrupt flag, which will cause the
        ongoing speech-to-text process to stop.
        """
        self._interrupt = True

    def _reset(self) -> None:
        """
        Resets the state variables of the speech-to-text recognizer, such as the list of events, recognition started
        flag, and interrupt flag.
        """
        # Reset the list of events that have been processed
        self._events: List[SpeechToTextOutput] = []

        # Reset the recognition threading.Event instance and set the interrupt flag to False
        self._interrupt: bool = False
        self._start_recognition: threading.Event = threading.Event()
        self._new_events: threading.Event = threading.Event()

    def _recognizer_events_connect(self) -> None:
        """
        Connects the speech-to-text recognizer events to their corresponding callbacks.
        """
        # Connect the session_started event to the _callback_started method
        self._recognizer.session_started.connect(self._callback_started)

        # Connect the recognized event to the _callback_word_boundary method
        self._recognizer.recognized.connect(self._process_recognized)

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for recognition started event. Signals that the recognition process has started.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the recognition started.
        """
        self._start_recognition.set()

    def _process_recognized(self, event: speechsdk.SpeechRecognitionEventArgs) -> None:
        """
        Processes the recognized speech event by appending it to the list of events and setting the new_events flag.

        Args:
            event (speechsdk.SpeechRecognitionEventArgs): The recognized speech event.
        """
        self._events.append(SpeechToTextOutput(event.result))
        self._new_events.set()

    def _process_callbacks(self, output: List[SpeechToTextOutput]) -> Generator[str, None, None]:
        """
        Processes the recognized speech events and appends them to the output list. Yields sentences as they are
        processed.

        Args:
            output (List[SpeechToTextOutput]): The list to store the recognized speech events.

        Yields:
            Generator[str, None, None]: A generator that yields sentences as they are processed.
        """
        # Initialize variables
        word_index = 0

        # Wait until the recognition has started before proceeding
        self._start_recognition.wait()

        # Continuously monitor the recognition progress
        while not self._interrupt:

            self._new_events.wait()
            self._new_events.clear()

            while not self._interrupt and word_index < len(self._events):
                event = self._events[word_index]
                output.append(event)
                word_index += 1
                yield str(event)

        # Stop the recognizer
        self._recognizer.stop_continuous_recognition()

    def listen(self) -> Generator[str, None, None]:
        """
        Starts the speech-to-text recognition process and yields sentences as they are recognized.

        Yields:
            Generator[str, None, None]: A generator that yields tuples of recognized sentences.
        """
        with self.__class__._listen_lock:

            # Reset all state attributes
            self._reset()

            # Prepare a list which will contain all the recognized input words.
            output = []
            self._outputs.append(output)

            # Starting the speech recognizer
            self._recognizer.start_continuous_recognition()

            # Continuously monitor the recognition progress in the main thread, yielding sentences as they are processed
            for block in self._process_callbacks(output):
                yield block
