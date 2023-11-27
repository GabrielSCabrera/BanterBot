import datetime
import logging
import os
import threading
import time
from typing import Generator, Optional

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat

from banterbot.data.enums import EnvVar, SpeechProcessingType, WordCategory
from banterbot.models.azure_neural_voice_profile import AzureNeuralVoiceProfile
from banterbot.models.phrase import Phrase
from banterbot.models.word import Word
from banterbot.types.timed_event import TimedEvent


class SpeechSynthesisService:
    """
    A class to handle text-to-speech synthesis utilizing Azure's Cognitive Services.

    This class provides an interface to convert text into speech using Azure's Cognitive Services. It supports various
    output formats, voices, and speaking styles. The synthesized speech can be interrupted, and the progress can be
    monitored in real-time.
    """

    # Create a lock that prevents race conditions when speaking
    _speech_lock = threading.Lock()

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

        # Set the interruption flag to the current time: if interruptions are raised, this will be updated.
        self._interrupt: int = time.perf_counter_ns()

        # Initialize events.
        self._start_synthesis: threading.Event = threading.Event()
        self._stop_synthesis: threading.Event = threading.Event()
        self._new_events: threading.Event = threading.Event()

        # Reset the state variables of the text-to-speech synthesizer
        self._reset()

    @property
    def speaking(self) -> bool:
        """
        If the current instance of `SpeechSynthesisService` is in the process of speaking, returns True. Otherwise,
        returns False.

        Args:
            bool: The speaking state of the current instance.
        """
        return self._start_synthesis.is_set()

    def interrupt(self, interrupt_ns: Optional[int] = None) -> None:
        """
        Interrupts an ongoing text-to-speech process, if any. This method sets the interrupt flag to the current time,
        which will cause any text-to-speech processes activated prior to the current time to stop.

        Args:
            interrupt_ns (Optional[int]): The time at which the recognizer was interrupted.
        """
        self._interrupt = max(interrupt_ns if interrupt_ns is not None else time.perf_counter_ns(), self._interrupt)
        logging.debug("SpeechSynthesisService synthesizer interrupted")

    def speak(self, input_string: str, voice: AzureNeuralVoiceProfile, style: str) -> Generator[Word, None, None]:
        """
        Speaks the specified text using the specified voice and style.

        This method converts the input text into speech using the specified voice and style. It yields the synthesized
        words one by one, along with their contextual information.

        Args:
            input_string (str): The input string that is to be converted into speech.
            voice (AzureNeuralVoice): The voice to be used.
            style (str): The speaking style to be applied.

        Yields:
            Word: A word with contextual information.
        """
        # Record the time at which the thread was initialized pre-lock, in order to account for future interruptions.
        init_time = time.perf_counter_ns()

        # Create SSML markup for the specified input_string, voice, and style
        ssml = self._create_ssml(input_string, voice, style)

        with self.__class__._speech_lock:
            # Continuously monitor the synthesis progress in the main thread, yielding words as they are uttered
            for word in self._callbacks_process(ssml, init_time):
                logging.debug(f"SpeechSynthesisService synthesizer processed word: `{word}`")
                yield word

            # Reset all state attributes
            self._reset()

    def speak_phrases(self, phrases: list[Phrase]) -> Generator[Word, None, None]:
        """
        Uses instances of class `Phrase` to allow for advanced SSML-based speech.

        This method converts the input text into speech using the specified instances of class `Phrase`. It yields the
        synthesized words one by one, along with their contextual information.

        Args:
            input_string (str): The input string that is to be converted into speech.

        Yields:
            Word: A word with contextual information.
        """
        # Record the time at which the thread was initialized pre-lock, in order to account for future interruptions.
        init_time = time.perf_counter_ns()

        # Create SSML markup for the specified input_string, voice, and style
        ssml = self._create_advanced_ssml(phrases)

        with self.__class__._speech_lock:
            # Continuously monitor the synthesis progress in the main thread, yielding words as they are uttered
            for word in self._callbacks_process(ssml, init_time):
                logging.debug(f"SpeechSynthesisService synthesizer processed word: `{word}`")
                yield word

            # Reset all state attributes
            self._reset()

    def _callback_completed(self, event: speechsdk.SessionEventArgs) -> None:
        """
        Callback function for synthesis completed event.
        Sets the synthesis completed flag to True.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis completed.
        """
        self._stop_synthesis.set()

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
            self._events.append(
                {
                    "event": event,
                    "time": 5e8 + 100 * event.audio_offset + 1e9 * event.duration.total_seconds() / event.word_length,
                    "word": self._process_event(event=event, first_word=len(self._events) == 0),
                }
            )

    def _callbacks_connect(self) -> None:
        """
        Connects the text-to-speech synthesizer events to their corresponding callbacks.

        This method connects the synthesis_started, synthesis_word_boundary, synthesis_canceled, and synthesis_completed
        events to their respective callback functions.
        """
        # Connect the synthesis_started event to the _callback_started method
        self._synthesizer.synthesis_started.connect(self._callback_started)

        # Connect the synthesis_word_boundary event to the _callback_word_boundary method
        self._synthesizer.synthesis_word_boundary.connect(self._callback_word_boundary)

        # Connect the synthesis_canceled and synthesis_completed events to the _callback_completed method
        self._synthesizer.synthesis_canceled.connect(self._callback_completed)
        self._synthesizer.synthesis_completed.connect(self._callback_completed)

    def _callbacks_process(self, ssml: str, init_time: int) -> Generator[Word, None, None]:
        """
        Monitors the synthesis progress and updates the output accordingly.

        This method continuously checks the synthesis progress and processes the boundaries. It then yields each
        processed word one by one.

        Args:
            ssml (str): The SSML command to be sent to the Speech Synthesizer.
            init_time (int): The time at which the speech was initialized.

        Yields:
            Word: A word with contextual information.
        """
        # Initialize variables
        idx = 0

        self._synthesizer.speak_ssml_async(ssml)

        logging.debug("SpeechSynthesisService synthesizer started")

        # Continuously monitor the synthesis progress
        while self._interrupt < init_time and (not self._stop_synthesis.is_set() or idx < len(self._events)):
            while (
                self._interrupt < init_time
                and idx < len(self._events)
                and time.perf_counter_ns() - self._start_synthesis_time >= self._events[idx]["time"]
            ):
                yield self._events[idx]["word"]
                idx += 1
            time.sleep(0.1)

        # Stop the synthesizer
        self._synthesizer.stop_speaking()
        logging.debug("SpeechSynthesisService synthesizer stopped")

    @classmethod
    def _create_ssml(cls, text: str, voice: str, style: Optional[str] = None) -> str:
        """
        Creates an SSML string from the specified text, voice, and style.

        Args:
            text (str): The input string that is to be converted into speech.
            voice (AzureNeuralVoice): The voice to be used.
            style (str, optional): The speaking style to be applied. Default is None.

        Returns:
            str: The SSML string.
        """
        # Start the SSML string with the required header and voice tag
        ssml = (
            '<speak version="1.0" '
            'xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" '
            'xml:lang="en-US">'
            f'<voice name="{voice.short_name}">'
        )

        # If a speaking style is specified, add the express-as tag
        if style:
            text = f'<mstts:express-as style="{style}">{text}</mstts:express-as>'

        # Add the text to the SSML string
        ssml += text

        # Close the voice and speak tags and return the SSML string
        ssml += "</voice></speak>"
        return ssml

    @classmethod
    def _create_advanced_ssml(cls, phrases: list[Phrase]) -> str:
        """
        Creates a more advanced SSML string from the specified list of `Phrase` instances, that customizes the emphasis,
        style, pitch, and rate of speech on a sub-sentence level, including pitch contouring between phrases.

        Args:
            phrases (list[Phrase]): Instances of class `Phrase` that contain data that can be converted into speech.

        Returns:
            str: The SSML string.
        """
        # Start the SSML string with the required header
        ssml = (
            '<speak version="1.0" '
            'xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" '
            'xml:lang="en-US">'
        )

        for n, phrase in enumerate(phrases):
            # Add contour only if there is a pitch transition
            if phrase.pitch is not None and phrase.pitch != phrases[min(n + 1, len(phrases) - 1)].pitch:
                # Set the contour to begin transition at 50% of the current phrase to match the pitch of the next one.
                contour = f"(50%,{phrase.pitch}) (80%,{phrases[n + 1].pitch})"
                pitch = f' contour="{contour}"'
            elif phrase.pitch is not None:
                pitch = f' pitch="{phrase.pitch}"'
            else:
                pitch = ""

            # Add the voice and other tags along with prosody
            ssml += f'<voice name="{phrase.voice.short_name}">'
            ssml += '<mstts:silence type="comma-exact" value="10ms"/>'
            ssml += '<mstts:silence type="Tailing-exact" value="0ms"/>'
            ssml += '<mstts:silence type="Sentenceboundary-exact" value="5ms"/>'
            ssml += '<mstts:silence type="Leading-exact" value="0ms"/>'

            if phrase.style and phrase.styledegree:
                ssml += f'<mstts:express-as style="{phrase.style}" styledegree="{phrase.styledegree}">'
            if pitch or phrase.rate:
                ssml += f'<prosody{pitch} rate="{phrase.rate if phrase.rate else ""}">'
            if phrase.emphasis:
                ssml += f'<emphasis level="{phrase.emphasis}">'

            ssml += f"{phrase.text}"

            if phrase.emphasis:
                ssml += "</emphasis>"
            if pitch or phrase.rate:
                ssml += "</prosody>"
            if phrase.style and phrase.styledegree:
                ssml += "</mstts:express-as>"
            ssml += "</voice>"

        # Close the voice and speak tags and return the SSML string
        ssml += "</speak>"
        return ssml

    def _process_event(self, event: speechsdk.SessionEventArgs, first_word: bool = False) -> Word:
        """
        Processes a synthesis boundary event and returns an instance of class Word.

        Args:
            event (speechsdk.SessionEventArgs): An event passed to the WordBoundary handle.
            first_word (bool): Indicate whether the words is the first in a sentence for correct whitespace handling.

        Returns:
            Word: The processed word with contextual information.
        """
        whitespace = ""
        if event.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Word:
            category = WordCategory.WORD
            if not first_word:
                whitespace = " "
        elif event.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Punctuation:
            category = WordCategory.PUNCTUATION

        word = Word(
            word=whitespace + event.text,
            offset=datetime.timedelta(microseconds=event.audio_offset / 10),
            duration=event.duration,
            category=category,
            source=SpeechProcessingType.TTS,
        )
        return word

    def _reset(self) -> None:
        """
        Resets the state variables of the text-to-speech synthesizer, such as the list of events, synthesis timer, the
        interrupt flag, the speaking flag, the synthesis completed flag, and synthesis started flag.
        """
        self._events: list[TimedEvent] = []
        self._start_synthesis_time = 0
        self._start_synthesis.clear()
        self._stop_synthesis.clear()
        self._new_events.clear()
