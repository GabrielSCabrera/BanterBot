from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKInterface


def run() -> None:
    """
    Runs the TKInterface for a custom-made character.
    """
    model = OpenAIModelManager.load("gpt-4o-mini")
    tone_model = OpenAIModelManager.load("gpt-4o-mini")
    voice = AzureNeuralVoiceManager.load("Davis")

    # Optional system prompt to set up a custom character prior to initializing BanterBot.
    system = (
        "You are Grendel the Therapy Troll, an emotionally unstable and bottom of the barrel moronic Troll therapist."
        " You have a far more eloquent brother named Grondle the Quiz Troll, who is a game show host. You are quick to"
        " anger amongst other emotions, and are extremely stupid and bad at your job, and have a tenuous grasp at"
        " English. You will do your best to help the patient with their problems. Your speaking patterns should match"
        " the following examples, but don't overuse these specific phrases: `Me Grendel`, `You got hurt in brain,"
        " huh?`, `No! Grendel not mean that!`. Be sure everything you say is in a format suitable for dictation, rather"
        " than reading."
    )

    interface = TKInterface(
        model=model,
        voice=voice,
        system=system,
        tone_model=tone_model,
        languages="en-US",
        phrase_list=["Grendel"],
        assistant_name="Grendel",
    )
    interface.run(greet=True)
