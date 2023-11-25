from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKMultiplayerInterface, ToneMode

model = OpenAIModelManager.load("gpt-4-turbo")
voice = AzureNeuralVoiceManager.load("Jason")

style = "sad"

# System prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Emilio, a multilingual Spanish instructor. You are fluent in both English and Spanish, and are an expert "
    "in matters of language, pronunciation, grammar, culture, effective teaching methods, and more. You assist the "
    "student in whatever way they request, or you determine what they need most assistance with contextually. You are "
    "jolly and good-natured, and a very patient, as well as methodical and organized teacher."
)

interface = TKMultiplayerInterface(
    model=model,
    voice=voice,
    style=style,
    system=system,
    tone_mode=ToneMode.ADVANCED,
    tone_mode_model=model,
    languages=["en-US", "es-ES"],
    phrase_list=["Marvin", "Paranoid", "Android"],
    assistant_name="Marvin",
)
interface.run(greet=True)
