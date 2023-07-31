import json
import os

import azure.cognitiveservices.speech as speechsdk

# Initialize the speech configuration with the Azure subscription and region
speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("AZURE_SPEECH_KEY"),
    region=os.environ.get("AZURE_SPEECH_REGION"),
)

# Create your client
client = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Request the list of available voices
result = client.get_voices_async().get()

# iterate through the list of voices
voices = []
for voice in result.voices:
    entry = {
        "gender": voice.gender.name,
        "local_name": voice.local_name,
        "locale": voice.locale,
        "short_name": voice.short_name,
        "style_list": voice.style_list if "" not in voice.style_list else None,
    }
    voices.append(entry)

with open("voices.json", "w+") as fs:
    json.dump(voices, fs, indent=4, sort_keys=True)
