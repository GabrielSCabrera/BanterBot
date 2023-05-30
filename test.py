import datetime
import json
import os
import time

import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("AZURE_SPEECH_KEY"),
    region=os.environ.get("AZURE_SPEECH_REGION"),
)
speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
speech_config.request_word_level_timestamps()

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)


def stop_cb(evt):
    print("CLOSING on {}".format(evt))
    speech_recognizer.stop_continuous_recognition()


# speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
speech_recognizer.recognized.connect(lambda evt: print(json.loads(evt.result.json)))
# speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}, {}, {}'.format(evt.result.json)))
# speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

t0 = datetime.datetime.now()
dt = datetime.timedelta(seconds=30)
t1 = t0 + dt

speech_recognizer.start_continuous_recognition()
while datetime.datetime.now() <= t1:
    time.sleep(0.1)
