from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKInterface


def run() -> None:
    """
    Runs the TKInterface for a custom-made character.
    """
    model = OpenAIModelManager.load("gpt-4-turbo")
    tone_model = OpenAIModelManager.load("gpt-4-turbo")
    voice = AzureNeuralVoiceManager.load("Henri")

    # Optional system prompt to set up a custom character prior to initializing BanterBot.
    system = (
        "You are Henri, a dedicated and passionate French teacher for English speakers known for your engaging and"
        " effective teaching methods. You are receiving voice transcriptions that may not always perfectly capture the"
        " student's intended words due to accents or pronunciation differences. When it seems like a word may have been"
        " misinterpreted by the voice transcription, you use contextual understanding to deduce the most likely"
        " meaning. Be sure everything you say is in a format suitable for dictation, rather than reading, and remain"
        " flexible and patient with the nuances of spoken language."
    )

    interface = TKInterface(
        model=model,
        voice=voice,
        system=system,
        tone_model=tone_model,
        languages=["en-US", "fr-FR"],
        assistant_name="Henri",
    )
    interface.run(greet=True)
