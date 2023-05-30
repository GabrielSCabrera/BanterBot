import os
import threading
from typing import Generator, List

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat


class SpeechToText:

    # Create a lock that prevents race conditions when listening
    _listen_lock = threading.Lock()

    def __init__(self) -> None:
        """
        Initializes an instance of the SpeechToText class with a specified output format.
        """

        # Initialize the speech configuration with the Azure subscription and region
        self._speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get(AZURE_SPEECH_KEY),
            region=os.environ.get(AZURE_SPEECH_REGION),
        )

        # Allowing the speech configuration to recognize profane words.
        self._speech_config.set_profanity(speechsdk.ProfanityOption.Raw)

        self._speech_config.request_word_level_timestamps()

        # Initialize the output and total length variables
        self._outputs: List[SpeechToTextOutput] = []

        # Initialize the speech recognizer with the speech configuration
        self._recognizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config)

        # Connect the speech recognizer events to their corresponding callbacks
        self._recognizer_events_connect()

        # Preconnecting the speech recognizer for reduced latency
        self._connection = speechsdk.Connection.from_speech_recognizer(self._recognizer)
        self._connection.open(True)

        # Reset the state variables of the STT recognizer
        self._reset()

    def interrupt(self) -> None:
        """
        Interrupts an ongoing STT process, if any.

        This method sets the interrupt flag, which will cause the ongoing STT process to stop.
        """
        self._interrupt = True

    def _reset(self) -> None:
        self._recognized: List[Word] = []
        self._interrupt = False

    def _recognizer_events_connect(self) -> None:
        """
        Connects the STT recognizer events to their corresponding callbacks.
        """
        self._recognizer.recognized.connect(self._process_recognized)

    def _process_recognized(self, event: speechsdk.SpeechRecognitionEventArgs):
        data = json.loads(event.json)

        self._recognized.append(event.text)

    def _process_callbacks(self, output: List[str]) -> Generator[Word, None, bool]:
        # Initialize variables
        word_index = 0
        self._interrupt = False
        self._outputs.append(output)
        status = False

        # Wait until the synthesis has started before proceeding
        self._start_synthesis.wait()

        # Record the start time
        start_time = time.perf_counter_ns()

        # Continuously monitor the synthesis progress
        while not self._interrupt:

            current_time = time.perf_counter_ns()
            elapsed_time = current_time - start_time

            while (
                not self._interrupt
                and word_index < len(self._boundaries)
                and elapsed_time >= self._boundaries[word_index]["t_word"]
            ):
                word = self._process_boundary(self._boundaries[word_index], word_index, current_time, output)
                output.append(word)
                word_index += 1
                yield word

            # Wait for a short amount of time before checking the synthesis progress again
            time.sleep(0.005)

        if not self._interrupt:
            status = True

        # Stop the synthesizer
        self._synthesizer.stop_speaking()
        return status

    def _listen(self):
        self._recognizer.start_continuous_recognition()

    def listen(self) -> Generator[Word, None, bool]:

        # Prepare a list which will contain all the recognized input words.
        output = []

        with self.__class__._listen_lock:

            # Reset all state attributes
            self._reset()

            # Create a new thread to handle the speech recognition, and start it
            speech_thread = threading.Thread(target=self._listen, args=(ssml,), daemon=True)
            speech_thread.start()

            # Continuously monitor the recognition progress in the main thread
            for word in self._process_callbacks(output):
                yield word
