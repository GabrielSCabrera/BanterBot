import logging
import threading
import time
from typing import Generator

import azure.cognitiveservices.speech as speechsdk

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
            if dt > 0:
                time.sleep(dt if dt >= 0 else 0)

            # Yield the word.
            yield item["word"]
            logging.debug(f"SpeechSynthesisHandler yielded word: `{item['word']}`")

    def close(self):
        self._synthesizer.stop_speaking_async()

    @classmethod
    def _phrases_to_ssml(cls, phrases: list[Phrase]) -> str:
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
