import asyncio

from banterbot.tts_synthesizer import TTSSynthesizer

TTS = TTSSynthesizer()

asyncio.run(TTS.speak("Hey There", "en-US-AriaNeural", "angry"))
