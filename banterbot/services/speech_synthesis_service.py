import datetime
import logging
import os
import threading
import time
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat

from banterbot.data.enums import EnvVar, SpeechProcessingType
from banterbot.handlers.speech_synthesis_handler import SpeechSynthesisHandler
from banterbot.handlers.stream_handler import StreamHandler
from banterbot.managers.stream_manager import StreamManager
from banterbot.models.phrase import Phrase
from banterbot.models.stream_log_entry import StreamLogEntry
from banterbot.models.word import Word
from banterbot.utils.closeable_queue import CloseableQueue


class SpeechSynthesisService:
    """
    The `SpeechSynthesisService` class provides an interface to convert text into speech using Azure's Cognitive
    Services. It supports various output formats, voices, and speaking styles. The synthesized speech can be
    interrupted, and the progress can be monitored in real-time.
    """

    # Create a lock that prevents race conditions when synthesizing speech
    _synthesis_lock = threading.Lock()

    def __init__(
        self,
        output_format: SpeechSynthesisOutputFormat = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
    ) -> None:
        """
        Initializes an instance of the `SpeechSynthesisService` class with a specified output format.

        Args:
            output_format (SpeechSynthesisOutputFormat, optional): The desired output format for the synthesized speech.
            Default is Audio16Khz32KBitRateMonoMp3.
        """
        self._init_synthesizer(output_format=output_format)

        # Initialize the StreamManager for handling streaming processes.
        self._stream_manager = StreamManager()

        # Indicates whether the current instance of `SpeechSynthesisService` is speaking.
        self._speaking = False

        # The latest interruption time.
        self._interrupt = 0

        # A list of active stream handlers.
        self._stream_handlers = []
        self._stream_handlers_lock = threading.Lock()

    def interrupt(self, kill: bool = False) -> None:
        """
        Interrupts the current speech synthesis process.

        Args:
            kill (bool): Whether the interruption should kill the queues or not.
        """
        self._interrupt = time.perf_counter_ns()
        with self._stream_handlers_lock:
            for handler in self._stream_handlers:
                handler.interrupt(kill=kill)
            self._stream_handlers.clear()
        logging.debug(f"SpeechSynthesisService Interrupted")

    def synthesize(self, phrases: list[Phrase], init_time: Optional[int] = None) -> StreamHandler:
        """
        Synthesizes the given phrases into speech and returns a handler for the stream of synthesized words.

        Args:
            phrases (list[Phrase]): The input phrases that are to be converted into speech.
            init_time (Optional[int]): The time at which the synthesis was initialized.

        Returns:
            StreamHandler: A handler for the stream of synthesized words.
        """
        # Record the time at which the synthesis was initialized pre-lock, in order to account for future interruptions.
        # Record the time at which the stream was initialized pre-lock, in order to account for future interruptions.
        init_time = time.perf_counter_ns() if init_time is None else init_time

        with self.__class__._synthesis_lock:
            if self._interrupt >= init_time:
                return tuple()
            else:
                self._queue = CloseableQueue()
                self._first_word = True

                iterable = SpeechSynthesisHandler(phrases=phrases, synthesizer=self._synthesizer, queue=self._queue)
                handler = self._stream_manager.stream(iterable=iterable, close_stream=iterable.close)
                with self._stream_handlers_lock:
                    self._stream_handlers.append(handler)
                return handler

    def _init_synthesizer(self, output_format: SpeechSynthesisOutputFormat) -> None:
        """
        Initializes the speech synthesizer.
        """
        logging.debug(f"SpeechSynthesisService initialized")

        # Initialize the speech configuration with the Azure subscription and region
        self._speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get(EnvVar.AZURE_SPEECH_KEY.value),
            region=os.environ.get(EnvVar.AZURE_SPEECH_REGION.value),
        )

        # Initialize the speech synthesizer with the speech configuration
        self._synthesizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config)

        # Set the speech synthesis output format to the specified output format
        self._speech_config.set_speech_synthesis_output_format(output_format)

        # Connect the speech synthesizer events to their corresponding callbacks
        self._callbacks_connect()

        # Creating a new instance of Connection class
        self._connection = speechsdk.Connection.from_speech_synthesizer(self._synthesizer)

        # Preconnecting the speech synthesizer for reduced latency
        self._connection.open(True)

    def _callback_completed(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis completed event. Signals that the synthesis process has been stopped/canceled.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis completed.
        """
        logging.debug("SpeechSynthesisService disconnected")
        self._speaking = False
        self._queue.close()

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis started event. Signals that the synthesis process has started.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.
        """
        logging.debug("SpeechSynthesisService connected")
        self._start_synthesis_time = time.perf_counter_ns()

    def _callback_word_boundary(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for word boundary event. Signals that a word boundary has been reached and provides the word
        and timing information.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the word boundary.
        """
        # Check if the type is not a sentence boundary
        if event.boundary_type != speechsdk.SpeechSynthesisBoundaryType.Sentence:
            # Add the event and timing information to the list of events
            self._queue.put({
                "event": event,
                "time": (
                    self._start_synthesis_time
                    + 5e8
                    + 100 * event.audio_offset
                    + 1e9 * event.duration.total_seconds() / event.word_length
                ),
                "word": Word(
                    word=(
                        event.text
                        if event.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Punctuation or self._first_word
                        else " " + event.text
                    ),
                    offset=datetime.timedelta(microseconds=event.audio_offset / 10),
                    duration=event.duration,
                    category=event.boundary_type,
                    source=SpeechProcessingType.TTS,
                ),
            })
            if self._first_word:
                self._first_word = False

    def _callbacks_connect(self):
        """
        Connect the synthesis events to their corresponding callback methods.
        """
        self._synthesizer.synthesis_started.connect(self._callback_started)
        self._synthesizer.synthesis_word_boundary.connect(self._callback_word_boundary)
        self._synthesizer.synthesis_canceled.connect(self._callback_completed)
        self._synthesizer.synthesis_completed.connect(self._callback_completed)
