import logging
import threading
import time
from typing import Generator, Optional

import azure.cognitiveservices.speech as speechsdk
import numba as nb

from banterbot.models.phrase import Phrase
from banterbot.models.word import Word
from banterbot.utils.closeable_queue import CloseableQueue


class SpeechSynthesisHandler:
    """
    A single-use class that handles the speech synthesis process. It is typically returned by the `speak` method of the
    `SpeechSynthesisService` class. It can be iterated over to yield the words as they are synthesized. It can also be
    closed to stop the speech synthesis process.
    """

    def __init__(self, phrases: list[Phrase], synthesizer: speechsdk.SpeechSynthesizer, queue: CloseableQueue) -> None:
        """
        Initializes a `SpeechSynthesisHandler` instance.

        Args:
            synthesizer (speechsdk.SpeechSynthesizer): The speech synthesizer to use for speech synthesis.
            queue (CloseableQueue): The queue to use for storing the words as they are synthesized.
        """
        self._synthesizer = synthesizer
        self._queue = queue
        self._iterating = False
        self._iterating_lock = threading.Lock()

        # Convert the phrases into SSML
        self._ssml = self._phrases_to_ssml(phrases)

    def __iter__(self) -> Generator[Word, None, None]:
        """
        Iterates over the words as they are synthesized, yielding each word as it is synthesized.

        Args:
            phrases (list[Phrase]): The phrases to be synthesized.

        Yields:
            Generator[Word, None, None]: The words as they are synthesized.
        """

        with self._iterating_lock:
            if self._iterating:
                raise RuntimeError(
                    "Cannot iterate over an already iterating instance of class `SpeechSynthesisHandler`"
                )
            self._iterating = True

        # Start synthesizing.
        self._synthesizer.speak_ssml_async(self._ssml)
        logging.debug("SpeechSynthesisHandler synthesizer started")

        # Process the words as they are synthesized.
        for item in self._queue:
            # Determine if a delay is needed to match the word's offset.
            dt = 1e-9 * (item["time"] - time.perf_counter_ns())
            # If a delay is needed, wait for the specified time.
            time.sleep(dt if dt >= 0 else 0)

            # Yield the word.
            yield item["word"]
            logging.debug(f"SpeechSynthesisHandler yielded word: `{item['word']}`")

    def close(self):
        self._synthesizer.stop_speaking_async()

    @staticmethod
    @nb.njit(cache=True)
    def _jit_phrases_to_ssml(
        texts: list[Optional[str]],
        short_names: list[Optional[str]],
        pitches: list[Optional[str]],
        rates: list[Optional[str]],
        styles: list[Optional[str]],
        styledegrees: list[Optional[str]],
        emphases: list[Optional[str]],
    ) -> str:
        """
        Creates a more advanced SSML string from the specified list of `Phrase` instances, that customizes the emphasis,
        style, pitch, and rate of speech on a sub-sentence level, including pitch contouring between phrases. Uses Numba
        to speed up the process.

        Args:
            texts (list[Optional[str]]): The texts to be synthesized.
            short_names (list[Optional[str]]): The short names of the voices to use for each phrase.
            pitches (list[Optional[str]]): The pitches to use for each phrase.
            rates (list[Optional[str]]): The rates to use for each phrase.
            styles (list[Optional[str]]): The styles to use for each phrase.
            styledegrees (list[Optional[str]]): The style degrees to use for each phrase.
            emphases (list[Optional[str]]): The emphases to use for each phrase.

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

        # Iterate over the phrases and add the SSML tags
        for n, (text, short_name, pitch, rate, style, styledegree, emphasis) in enumerate(
            zip(texts, short_names, pitches, rates, styles, styledegrees, emphases)
        ):
            # Add contour only if there is a pitch transition
            if pitch:
                if n < len(pitches) - 1 and pitches[n + 1] and pitch != pitches[n + 1]:
                    # Set the contour to begin transition at 50% of the current phrase to match the pitch of the next one.
                    pitch = ' contour="(50%,' + pitch + ") (80%," + pitches[n + 1] + ')"'
                else:
                    pitch = ' pitch="' + pitch + '"'
            else:
                pitch = ""

            # Add the voice and other tags along with prosody
            ssml += '<voice name="' + short_name + '">'
            ssml += '<mstts:silence type="comma-exact" value="10ms"/>'
            ssml += '<mstts:silence type="Tailing-exact" value="0ms"/>'
            ssml += '<mstts:silence type="Sentenceboundary-exact" value="5ms"/>'
            ssml += '<mstts:silence type="Leading-exact" value="0ms"/>'

            # Add the express-as tag if style and styledegree are specified
            if style and styledegree:
                ssml += '<mstts:express-as style="' + style + '" styledegree="' + styledegree + '">'
            if pitch or rate:
                rate_value = rate if rate else ""
                ssml += "<prosody" + pitch + ' rate="' + rate_value + '">'
            if emphasis:
                ssml += '<emphasis level="' + emphasis + '">'

            ssml += text

            # Close the tags
            if emphasis:
                ssml += "</emphasis>"
            if pitch or rate:
                ssml += "</prosody>"
            if style and styledegree:
                ssml += "</mstts:express-as>"
            ssml += "</voice>"

        # Close the voice and speak tags and return the SSML string
        ssml += "</speak>"
        return ssml

    @classmethod
    def _phrases_to_ssml(cls, phrases: list[Phrase]) -> str:
        """
        Creates a more advanced SSML string from the specified list of `Phrase` instances, that customizes the emphasis,
        style, pitch, and rate of speech on a sub-sentence level, including pitch contouring between phrases. Calls the
        'jit_phrases_to_ssml' method to speed up the process using Numba.

        Args:
            phrases (list[Phrase]): Instances of class `Phrase` that contain data that can be converted into speech.

        Returns:
            str: The SSML string.
        """
        texts, short_names, pitches, rates, styles, styledegrees, emphases = zip(
            *[
                (
                    phrase.text,
                    phrase.voice.short_name,
                    phrase.pitch,
                    phrase.rate,
                    phrase.style,
                    phrase.styledegree,
                    phrase.emphasis,
                )
                for phrase in phrases
            ]
        )

        return cls._jit_phrases_to_ssml(texts, short_names, pitches, rates, styles, styledegrees, emphases)
