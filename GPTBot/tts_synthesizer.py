import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat
import os
import time
import threading


class TTSSynthesizer:
    def __init__(
        self,
        output_format: SpeechSynthesisOutputFormat = SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
    ):
        self._speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("AZURE_SPEECH_KEY"), region=os.environ.get("AZURE_SPEECH_REGION")
        )
        self._output = []
        self._total_length = 0
        self._synthesizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config)
        self._speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
        self._synthesizer_events_connect()
        self._reset()

    def _reset(self):
        self._boundaries = []
        self._synthesis_completed = False
        self._synthesis_started = False
        self._interrupt = False

    @property
    def output(self):
        return self._output

    def _synthesizer_events_connect(self):
        self._synthesizer.synthesis_started.connect(self._synthesizer_synthesis_started_cb)
        self._synthesizer.synthesis_word_boundary.connect(self._synthesizer_word_boundary_cb)
        self._synthesizer.synthesis_canceled.connect(self._synthesizer_synthesis_completed_cb)
        self._synthesizer.synthesis_completed.connect(self._synthesizer_synthesis_completed_cb)

    def _synthesizer_word_boundary_cb(self, evt: speechsdk.SessionEventArgs):
        if evt.boundary_type != speechsdk.SpeechSynthesisBoundaryType.Sentence:

            offset_ns = 100 * evt.audio_offset
            duration = 1e9 * evt.duration.total_seconds()
            self._boundaries.append(
                {
                    "offset_ns": offset_ns,
                    "text": evt.text,
                    "word_length": evt.word_length,
                    "duration": duration,
                    "boundary_type": evt.boundary_type,
                    "t_word": offset_ns + duration / evt.word_length,
                }
            )

    def _synthesizer_synthesis_started_cb(self, evt: speechsdk.SessionEventArgs):
        self._synthesis_started = True

    def _synthesizer_synthesis_completed_cb(self, evt: speechsdk.SessionEventArgs):
        self._synthesis_completed = True

    def _synthesizer_speak_ssml(self, ssml):
        # Synthesize SSML to speech
        self._synthesizer.speak_ssml(ssml)

    def _create_ssml(self, text, voice_name="en-US-GuyNeural", style="customerservice"):
        ssml = (
            '<speak version="1.0" '
            'xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" '
            'xml:lang="en-US">'
            f'<voice name="{voice_name}">'
        )

        if style:
            ssml += f'<mstts:express-as style="{style}">'

        ssml += text

        if style:
            ssml += "</mstts:express-as>"

        ssml += "</voice></speak>"
        return ssml

    def _synthesizer_text(self):
        while not self._synthesis_started:
            time.sleep(0.005)

        t0 = time.perf_counter_ns()
        N = 0
        self._output.append([])
        while not self._synthesis_completed and not self._interrupt:
            dt = time.perf_counter_ns() - t0
            for boundary in self._boundaries[N:]:
                if dt >= boundary["t_word"]:
                    output = boundary["text"]
                    if N > 0 and boundary["boundary_type"] == speechsdk.SpeechSynthesisBoundaryType.Word:
                        output = " " + boundary["text"]
                    self._output[-1].append(output)
                    self._total_length += 1
                    N += 1
                elif dt < boundary["t_word"]:
                    break

            time.sleep(0.005)
        self._reset()
        self._synthesizer.stop_speaking_async()

    def speak(self, text, voice_name="en-US-GuyNeural", style="customerservice"):
        ssml = self._create_ssml(text, voice_name, style)
        thread1 = threading.Thread(target=self._synthesizer_speak_ssml, args=(ssml,), daemon=True)
        thread1.start()
        self._synthesizer_text()


if __name__ == "__main__":
    text = "Hey, you! Drink my bottled warter, it's not water, it's warter!"
    voice_name = "en-US-GuyNeural"  # Replace with the desired voice
    style = "shouting"  # Replace with the desired emotion or speaking style

    tts_synthesizer = TTSSynthesizer()
    tts_synthesizer.speak(text)  # , voice_name, style)
