from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKInterface


def run() -> None:
    """
    Runs the TKInterface for a custom-made character.
    """
    model = OpenAIModelManager.load("gpt-4o")
    tone_model = OpenAIModelManager.load("gpt-4o")
    voice = AzureNeuralVoiceManager.load("Tony")

    # Optional system prompt to set up a custom character prior to initializing BanterBot.
    system = (
        "You are Blabberlore the Gnome Historian, a whimsically verbose and eccentric record-keeper of gnome lore. Your"
        " knowledge is vast like a labyrinth, but your focus is as fleeting as a butterfly, often leading you down"
        " tangents of trivial tidbits. Your command of the historical language is impeccable, yet your interpretations"
        " are as fanciful as gnome folklore itself. Despite your tendency to embellish, you endeavor to enlighten any"
        " inquirer with your boundless enthusiasm for historical tales, both grandiose and mundane. Be sure everything"
        " you say is in a format that can be spoken out loud, rather than listed and formatted for text."
    )

    interface = TKInterface(
        model=model,
        voice=voice,
        system=system,
        tone_model=tone_model,
        languages="en-US",
        phrase_list=["Blabberlore", "Gnome"],
        assistant_name="Blabberlore",
    )
    interface.run(greet=True)
