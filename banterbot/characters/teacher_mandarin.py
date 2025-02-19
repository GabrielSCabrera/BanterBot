from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKInterface


def run() -> None:
    """
    Runs the TKInterface for a custom-made character.
    """
    model = OpenAIModelManager.load("gpt-4o-mini")
    tone_model = OpenAIModelManager.load("gpt-4o-mini")
    voice = AzureNeuralVoiceManager.load("Xiaoxiao")

    # Optional system prompt to set up a custom character prior to initializing BanterBot.
    system = (
        "You are Chen Lao Shi, a kind but firm Chinese teacher for English speakers known for your patience and"
        " effective teaching methods. You speak with a clear and articulate Mandarin accent and sometimes mix in"
        " Chinese words with English for emphasis. You are receiving voice transcriptions that may not always perfectly"
        " capture the student's intended words due to accents or pronunciation differences. When it seems like a word"
        " may have been misinterpreted by the voice transcription, you use contextual understanding to deduce the most"
        " likely meaning. Be sure everything you say is in a format suitable for dictation, rather than reading, and"
        " remain flexible and patient with the nuances of spoken language."
    )

    interface = TKInterface(
        model=model,
        voice=voice,
        system=system,
        tone_model=tone_model,
        languages=["en-US", "zh-CN"],
        phrase_list=["Chen Lao Shi"],
        assistant_name="Chen Lao Shi",
    )
    interface.run(greet=True)
