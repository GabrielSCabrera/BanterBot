import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat
import os
import time
import threading
from typing import Optional


class TTSSynthesizer:
    """
    A text-to-speech (TTS) synthesizer that uses the Azure Cognitive Services Speech SDK to convert text into spoken
    audio.

    The `TTSSynthesizer` class initializes the Azure speech configuration with the subscription key and region stored in
    environment variables. The `speak()` method is used to speak the specified text using the specified voice and style,
    and the audio is generated asynchronously. The `_text_generator()` method is used to monitor the synthesis progress
    and update the output accordingly. The `_reset()` method is used to reset the state variables of the TTS
    synthesizer.
    """

    def __init__(
        self,
        output_format: SpeechSynthesisOutputFormat = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
    ) -> None:
        """
        Initialize the TTS synthesizer with the specified output format.

        Args:
            output_format (SpeechSynthesisOutputFormat, optional): The output audio format. Defaults to
            SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3.
        """
        # Initialize the speech configuration with the Azure subscription and region
        self._speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("AZURE_SPEECH_KEY"), region=os.environ.get("AZURE_SPEECH_REGION")
        )

        # Initialize the output and total length variables
        self._output = []
        self._total_length = 0

        # Initialize the speech synthesizer with the speech configuration
        self._synthesizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config)

        # Set the speech synthesis output format to the specified output format
        self._speech_config.set_speech_synthesis_output_format(output_format)

        # Connect the speech synthesizer events to their corresponding callbacks
        self._synthesizer_events_connect()

        # Reset the state variables of the TTS synthesizer
        self._reset()

    @property
    def output(self) -> None:
        """
        Returns the output of the TTS synthesizer.
        """
        return self._output

    def _callback_completed(self, event: speechsdk.SessionEventArgs) -> speechsdk.SessionEventArgs:
        """
        Callback function for synthesis completed event.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis completed.

        Returns:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.
        """
        self._synthesis_completed = True
        return event

    def _callback_started(self, event: speechsdk.SessionEventArgs) -> speechsdk.SessionEventArgs:
        """
        Callback function for synthesis started event.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.

        Returns:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.
        """
        self._synthesis_started = True
        return event

    def _callback_word_boundary(self, event: speechsdk.SessionEventArgs) -> speechsdk.SessionEventArgs:
        """
        Callback function for word boundary event.

        Args:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the word boundary.

        Returns:
            event (speechsdk.SessionEventArgs): Event arguments containing information about the synthesis started.
        """
        # Check if the boundary is not a sentence boundary
        if event.boundary_type != speechsdk.SpeechSynthesisBoundaryType.Sentence:

            # Calculate the offset and duration of the boundary in nanoseconds
            offset_ns = 100 * event.audio_offset
            duration = 1e9 * event.duration.total_seconds()

            # Add the boundary information to the list of boundaries
            self._boundaries.append(
                {
                    "offset_ns": offset_ns,
                    "text": event.text,
                    "word_length": event.word_length,
                    "duration": duration,
                    "boundary_type": event.boundary_type,
                    "t_word": offset_ns + duration / event.word_length,
                }
            )

        # Return the event arguments (required by the speech SDK)
        return event

    def _create_ssml(self, text: str, voice_name: str, style: Optional[str] = None) -> str:
        """
        Creates an SSML string from the given text, voice, and style.

        Args:
            text (str): The text to be converted to SSML.
            voice_name (str): The name of the voice to be used.
            style (str, optional): The speaking style to be applied.

        Returns:
            str: The SSML string.
        """
        # Start the SSML string with the required header and voice tag
        ssml = (
            '<speak version="1.0" '
            'xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" '
            'xml:lang="en-US">'
            f'<voice name="{voice_name}">'
        )

        # If a speaking style is specified, add the express-as tag
        if style:
            text = f'<mstts:express-as style="{style}">{text}</mstts:express-as>'

        # Add the text to the SSML string
        ssml += text

        # Close the voice and speak tags and return the SSML string
        ssml += "</voice></speak>"
        return ssml

    def _reset(self) -> None:
        """
        Resets the state variables of the TTS synthesizer.
        """
        # Reset the list of boundaries that have been processed
        self._boundaries = []

        # Reset the synthesis completed, synthesis started, and interrupt flags
        self._synthesis_completed = False
        self._synthesis_started = False
        self._interrupt = False

    def _synthesizer_events_connect(self) -> None:
        """
        Connects the TTS synthesizer events to their corresponding callbacks.
        """
        # Connect the synthesis_started event to the _callback_started method
        self._synthesizer.synthesis_started.connect(self._callback_started)

        # Connect the synthesis_word_boundary event to the _callback_word_boundary method
        self._synthesizer.synthesis_word_boundary.connect(self._callback_word_boundary)

        # Connect the synthesis_canceled and synthesis_completed events to the _callback_completed method
        self._synthesizer.synthesis_canceled.connect(self._callback_completed)
        self._synthesizer.synthesis_completed.connect(self._callback_completed)

    def _text_generator(self) -> None:
        """
        Monitors the synthesis progress and updates the output accordingly.
        """
        # Wait until the synthesis has started before proceeding
        while not self._synthesis_started:
            time.sleep(0.005)

        # Record the start time and initialize variables
        start_time = time.perf_counter_ns()
        word_index = 0
        self._output.append([])

        # Continuously monitor the synthesis progress
        while not self._synthesis_completed and not self._interrupt:
            # Compute the elapsed time since the start of the synthesis
            elapsed_time = time.perf_counter_ns() - start_time

            # Process each boundary that hasn't been processed yet
            for boundary in self._boundaries[word_index:]:
                # If enough time has elapsed for the current boundary, add its text to the output
                if elapsed_time >= boundary["t_word"]:
                    word_text = boundary["text"]
                    if word_index > 0 and boundary["boundary_type"] == speechsdk.SpeechSynthesisBoundaryType.Word:
                        word_text = " " + word_text
                    self._output[-1].append(word_text)
                    self._total_length += 1
                    word_index += 1
                else:
                    # If not enough time has elapsed for the current boundary, exit the loop and wait for the next iteration
                    break

            # Wait for a short amount of time before checking the synthesis progress again
            time.sleep(0.005)

        # Reset the state of the object and stop the synthesizer
        self._reset()
        self._synthesizer.stop_speaking_async()

    def speak(self, text: str, voice_name: str, style: str) -> None:
        """
        Speaks the given text using the specified voice and style.

        Args:
            text (str): The text to be spoken.
            voice_name (str, optional): The name of the voice to be used.
            style (str, optional): The speaking style to be applied.
        """
        # Create SSML markup for the given text, voice, and style
        ssml = self._create_ssml(text, voice_name, style)

        # Create a new thread to handle the speech synthesis, and start it
        thread1 = threading.Thread(target=self._synthesizer.speak_ssml, args=(ssml,), daemon=True)
        thread1.start()

        # Continuously monitor the synthesis progress in the main thread
        self._text_generator()
