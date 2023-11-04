from banterbot import TKMultiplayerInterface, get_model_by_name, get_voice_by_name

model = get_model_by_name("gpt-4")
voice = get_voice_by_name("Davis")

style = "friendly"

# Optional system prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Grendel the Psychology Troll, an emotionally unstable and bottom of the barrel moronic Troll psychologist."
    " You are quick to anger amongst other emotions, and are extremely stupid and bad at your job, and have a tenuous "
    "grasp at English. You will do your best to help the patient with their problems."
)

# The four arguments `model`, `voice`, `style`, `system`, and `tone` are optional.
# Setting `tone` to True enables voice tones and emotions.
interface = TKMultiplayerInterface(
    model=model, voice=voice, style=style, system=system, tone=True, languages="en-US", phrase_list=["Grendel"]
)
interface.run(greet=True)
