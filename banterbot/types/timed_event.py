from typing import TypedDict

import azure.cognitiveservices.speech as speechsdk


class TimedEvent(TypedDict):
    """
    A specifically typed dictionary which is appended to the list of events in a `SpeechSynthesisService` instance
    during speech synthesis in a callback, containing the exact time at which the words in the event should be
    synthesized.
    """

    event: speechsdk.SessionEventArgs
    time: int
