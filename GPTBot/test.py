import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat

import os

speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("AZURE_SPEECH_KEY"), region=os.environ.get("AZURE_SPEECH_REGION")
)

text = "The Speech SDK uses a websocket to communicate with the service. Ideally, the network latency should be one route trip time (RTT). If the connection is newly established, the network latency will include extra time to establish the connection. The establishment of a websocket connection needs the TCP handshake, SSL handshake, HTTP connection, and protocol upgrade, which introduces time delay. To avoid the connection latency, we recommend pre-connecting and reusing the SpeechSynthesizer."

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
result = speech_synthesizer.start_speaking_text_async(text).get()
audio_data_stream = speechsdk.AudioDataStream(result)
audio_buffer = bytes(16000)
filled_size = audio_data_stream.read_data(audio_buffer)
while filled_size > 0:
    print("{} bytes received.".format(filled_size))
    filled_size = audio_data_stream.read_data(audio_buffer)
