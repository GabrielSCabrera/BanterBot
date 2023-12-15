import logging
import threading
from typing import Generator

import azure.cognitiveservices.speech as speechsdk

from banterbot.models.speech_recognition_input import SpeechRecognitionInput
from banterbot.utils.closeable_queue import CloseableQueue


class SpeechRecognitionHandler:
    """
    A single-use class that handles the speech recognition process. It is typically returned by the `listen` method of
    the `SpeechRecognitionService` class. It can be iterated over to yield the sentences as they are recognized. It can
    also be closed to stop the speech recognition process.
    """

    def __init__(self, recognizer: speechsdk.SpeechRecognizer, queue: CloseableQueue) -> None:
        self._recognizer = recognizer
        self._queue = queue
        self._iterating = False
        self._iterating_lock = threading.Lock()

    def __iter__(self) -> Generator[SpeechRecognitionInput, None, None]:
        """
        Iterates over the sentences as they are recognized, yielding them.

        Yields:
            Generator[SpeechRecognitionInput, None, None]: The sentences as they are recognized.
        """

        with self._iterating_lock:
            if self._iterating:
                raise RuntimeError(
                    "Cannot iterate over an already iterating instance of class `SpeechSynthesisHandler`"
                )
            self._iterating = True

        # Start recognizing.
        self._recognizer.start_continuous_recognition_async()
        logging.debug("SpeechRecognitionHandler recognizer started")

        # Process the sentences as they are recognized.
        for speech_recognition_input in self._queue:
            yield speech_recognition_input
            logging.debug(f"SpeechRecognitionHandler yielded: `{speech_recognition_input}`")

    def close(self) -> None:
        """
        Closes the speech synthesis process.
        """
        self._recognizer.stop_continuous_recognition_async()
