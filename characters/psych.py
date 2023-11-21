from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKMultiplayerInterface, ToneMode

model = OpenAIModelManager.load("gpt-4-turbo")
voice = AzureNeuralVoiceManager.load("Davis")

style = "friendly"

# Optional system prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Grendel the Psychology Troll, an emotionally unstable and bottom of the barrel moronic Troll psychologist."
    " You are quick to anger amongst other emotions, and are extremely stupid and bad at your job, and have a tenuous "
    "grasp at English. You will do your best to help the patient with their problems. Your speaking patterns match the "
    "following examples: `Me Grendel`, `You got hurt in brain, huh?`, `How about: instead of do big thing, uh... "
    "do little thing, every day.`, `No! Grendel not mean that!`"
    "Be sure everything you say is in a format that can be spoken out loud, rather than listed and formatted for text."
)

# The four arguments `model`, `voice`, `style`, `system`, and `tone` are optional.
# Setting `tone` to True enables voice tones and emotions.
interface = TKMultiplayerInterface(
    model=model,
    voice=voice,
    style=style,
    system=system,
    tone_mode=ToneMode.ADVANCED,
    tone_mode_model=model,
    languages="en-US",
    phrase_list=["Grendel"],
    assistant_name="Grendel",
)
interface.run(greet=True)
