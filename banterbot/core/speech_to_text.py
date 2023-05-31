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

        # Preconnecting the speech recognizer for reduced latency
        self._connection = speechsdk.Connection.from_recognizer(self._recognizer)
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
        self._interrupt = False
        self._start_recognition = threading.Event()
        self._new_events = threading.Event()

    def _recognizer_events_connect(self) -> None:
        """
        Connects the speech-to-text recognizer events to their corresponding callbacks.
        """
        self._recognizer.recognized.connect(self._process_recognized)

    def _process_recognized(self, event: speechsdk.SpeechRecognitionEventArgs) -> None:
        """
        Processes the recognized speech event by appending it to the list of events and setting the new_events flag.

        Args:
            event (speechsdk.SpeechRecognitionEventArgs): The recognized speech event.
        """
        self._events.append(SpeechToTextOutput(event.result))
        self._new_events.set()

    def _process_callbacks(self, output: List[SpeechToTextOutput]) -> Generator[Word, None, bool]:
        """
        Processes the recognized speech events and appends them to the output list. Yields sentences as they are
        processed.

        Args:
            output (List[SpeechToTextOutput]): The list to store the recognized speech events.

        Yields:
            Generator[Word, None, bool]: A generator that yields sentences as they are processed.
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
                yield event.sents

        # Stop the recognizer
        self._recognizer.stop_continuous_recognition()

    def _listen(self) -> None:
        """
        Starts the speech recognizer for continuous recognition.
        """
        self._recognizer.start_continuous_recognition()

    def listen(self) -> Generator[Tuple[str, ...], None, bool]:
        """
        Starts the speech-to-text recognition process and yields sentences as they are recognized.

        Yields:
            Generator[Tuple[str, ...], None, bool]: A generator that yields tuples of recognized sentences.
        """
        with self.__class__._listen_lock:

            # Create a new thread to handle the speech recognition, and start it
            listener_thread = threading.Thread(target=self._listen, daemon=True)

            # Reset all state attributes
            self._reset()

            # Starting the speech recognizer
            listener_thread.start()

            # Prepare a list which will contain all the recognized input words.
            output = []
            self._outputs.append(output)

            # Continuously monitor the recognition progress in the main thread, yielding sentences as they are processed
            for block in self._process_callbacks(output):
                yield block
