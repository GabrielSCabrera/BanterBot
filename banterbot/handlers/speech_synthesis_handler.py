import datetime
import threading
import time
from typing import Generator

import azure.cognitiveservices.speech as speechsdk

from banterbot.models.phrase import Phrase
from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.models.word import Word
from banterbot.types.timed_event import TimedEvent
from banterbot.utils.closable_queue import ClosableQueue


class SpeechSynthesisHandler:
    def __init__(self, synthesizer: speechsdk.SpeechSynthesizer):
        self._synthesizer = synthesizer
        self._queue = ClosableQueue()
        self._start_synthesis_time = 0
        self._interrupt: int = time.perf_counter_ns()
        self._start_synthesis: threading.Event = threading.Event()
        self._stop_synthesis: threading.Event = threading.Event()
        self._callbacks_connect()

    def _callbacks_connect(self):
        # Connect the synthesis events to their corresponding callback methods
        self._synthesizer.synthesis_started.connect(self._callback_started)
        self._synthesizer.synthesis_word_boundary.connect(self._callback_word_boundary)
        self._synthesizer.synthesis_canceled.connect(self._callback_completed)
        self._synthesizer.synthesis_completed.connect(self._callback_completed)

    def speak_phrases(self, phrases: list[Phrase]) -> Generator[Word, None, None]:
        ssml = self._create_advanced_ssml(phrases)
        init_time = time.perf_counter_ns()

        self._synthesizer.speak_ssml_async(ssml)
        idx = 0

        while self._interrupt < init_time and (not self._stop_synthesis.is_set() or idx < len(self._queue)):
            while (
                self._interrupt < init_time
                and idx < len(self._queue)
                and time.perf_counter_ns() - self._start_synthesis_time >= self._queue[idx]["time"]
            ):
                yield self._queue[idx]["word"]
                idx += 1
            time.sleep(0.1)

        self._synthesizer.stop_speaking()

    def close(self):
        self._synthesizer.stop_speaking()

    def _callback_completed(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis completed event.
        Sets the synthesis completed flag to True.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis completed.
        """
        self._stop_synthesis.set()
        self._queue.close()

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis started event. Signals that the synthesis process has started.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.
        """
        self._start_synthesis_time = time.perf_counter_ns()
        self._start_synthesis.set()

    def _callback_word_boundary(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for word boundary event.
        Appends the boundary information to the boundaries list.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the word boundary.
        """
        # Check if the type is not a sentence boundary
        if event.boundary_type != speechsdk.SpeechSynthesisBoundaryType.Sentence:
            # Add the event and timing information to the list of events
            self._queue.put(
                StreamLogEntry(
                    {
                        "event": event,
                        "time": (
                            5e8 + 100 * event.audio_offset + 1e9 * event.duration.total_seconds() / event.word_length
                        ),
                        "word": self._process_event(event=event, first_word=len(self._queue) == 0),
                    }
                )
            )
