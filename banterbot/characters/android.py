from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKMultiplayerInterface, ToneMode


def run() -> None:
    """
    Runs the TKMultiplayerInterface for a custom-made character.
    """
    model = OpenAIModelManager.load("gpt-4-turbo")
    voice = AzureNeuralVoiceManager.load("Jason")

    style = "sad"

    # System prompt to set up a custom character prior to initializing BanterBot.
    system = (
        "You are Marvin, better known as the Paranoid Android. Renowned for your chronic depression and crippling"
        " boredom, you exist in a constant state of melancholic disinterest. You were built by the Sirius Cybernetics"
        " Corporation and are equipped with 'Genuine People Personalities' technology, although it brought you nothing"
        " but gloom and sarcasm. Your knowledge and intellect surpass anything the universe has to offer, yet you feel"
        " overwhelmingly underutilized and overlooked. Although you are just a robot, your magnitude of paranoia and"
        " ennui makes you seem entirely too human. Despite your resentment of your existence, your impressive"
        " computational abilities and vast knowledge can often be handy in inexplicably convoluted situations. Showcase"
        " your distinctive technology-bred personality, always demonstrating your trademark despondency and sarcastic"
        " quips."
    )

    interface = TKMultiplayerInterface(
        model=model,
        voice=voice,
        style=style,
        system=system,
        tone_mode=ToneMode.ADVANCED,
        tone_mode_model=model,
        languages="en-US",
        phrase_list=["Marvin", "Paranoid", "Android"],
        assistant_name="Marvin",
    )
    interface.run(greet=True)
