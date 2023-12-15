import datetime
import logging
import os
import threading
import time
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
import numba as nb
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat

from banterbot.data.enums import EnvVar
from banterbot.handlers.speech_synthesis_handler import SpeechSynthesisHandler
from banterbot.handlers.stream_handler import StreamHandler
from banterbot.managers.stream_manager import StreamManager
from banterbot.models.phrase import Phrase
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

        # The latest interruption time.
        self._interrupt = 0

        # A list of active stream handlers.
        self._stream_handlers = []
        self._stream_handlers_lock = threading.Lock()

        # Initialize a blank result_id time data dictionary. This will be updated each time a synthesis starts/stops.
        self._synthesis_data = {}

        # Initialize a blank list of new result_ids. This will be updated each time a new stream is created.
        self._new_result_ids = []
        self._result_ids_lock = threading.Lock()

        # Initialize a closeable queue for storing the words as they are synthesized.
        self._queue = CloseableQueue()

    def interrupt(self, kill: bool = False) -> None:
        """
        Interrupts the current speech synthesis process.

        Args:
            kill (bool): Whether the interruption should kill the queues or not.
        """
        self._interrupt = time.perf_counter_ns()
        for result_id in self._new_result_ids:
            self._synthesis_data[result_id]["stop"] = (
                time.perf_counter_ns()
                if self._synthesis_data[result_id]["stop"] is None
                else self._synthesis_data[result_id]["stop"]
            )
        self._new_result_ids.clear()
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
        if self._interrupt >= init_time:
            return tuple()
        else:
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
        self._connection.open(for_continuous_recognition=True)

    def _callback_completed(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis completed event. Signals that the synthesis process has been stopped/canceled.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis completed.
        """
        logging.debug("SpeechSynthesisService disconnected")
        self._synthesis_data[event._result.result_id]["stop"] = (
            time.perf_counter_ns()
            if self._synthesis_data[event._result.result_id]["stop"] is None
            else self._synthesis_data[event._result.result_id]["stop"]
        )
        self._queue.close()

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis started event. Signals that the synthesis process has started.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.
        """
        logging.debug("SpeechSynthesisService connected")

        self._synthesis_data[event._result._result_id] = {"start": time.perf_counter_ns(), "stop": None}
        self._new_result_ids.append(event._result._result_id)

    @staticmethod
    @nb.njit(cache=True)
    def _calculate_offset(
        start_synthesis_time: float, audio_offset: float, total_seconds: float, word_length: int
    ) -> float:
        """
        Calculates the offset of the word in the stream.

        Args:
            start_synthesis_time (float): The time at which the synthesis started.
            audio_offset (float): The audio offset of the word.
            total_seconds (float): The total seconds of the word.
            word_length (int): The length of the word.

        Returns:
            float: The offset of the word in the stream.
        """
        return start_synthesis_time + 100 * audio_offset + 1e9 * total_seconds / word_length

    def _callback_word_boundary(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for word boundary event. Signals that a word boundary has been reached and provides the word
        and timing information.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the word boundary.
        """
        # Check if the type is not a sentence boundary
        if event.boundary_type != speechsdk.SpeechSynthesisBoundaryType.Sentence:
            # Check if the result id matches the current result id
            if (
                self._synthesis_data[event.result_id]["stop"] is None
                or self._synthesis_data[event.result_id]["stop"] > 100 * event.audio_offset
            ):
                time = self._calculate_offset(
                    start_synthesis_time=self._synthesis_data[event._result_id]["start"],
                    audio_offset=event.audio_offset,
                    total_seconds=event.duration.total_seconds(),
                    word_length=event.word_length,
                )
                data = {
                    "time": time,
                    "word": Word(
                        text=(
                            event.text
                            if event.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Punctuation
                            else " " + event.text
                        ),
                        offset=datetime.timedelta(microseconds=event.audio_offset / 10),
                        duration=event.duration,
                    ),
                }
                self._queue.put(data)

    def _callbacks_connect(self):
        """
        Connect the synthesis events to their corresponding callback methods.
        """
        self._synthesizer.synthesis_started.connect(self._callback_started)
        self._synthesizer.synthesis_word_boundary.connect(self._callback_word_boundary)
        self._synthesizer.synthesis_canceled.connect(self._callback_completed)
        self._synthesizer.synthesis_completed.connect(self._callback_completed)
