from banterbot.tts_synthesizer import TTSSynthesizer
import asyncio

TTS = TTSSynthesizer()

asyncio.run(TTS.speak("Hey There", "en-US-AriaNeural", "angry"))
