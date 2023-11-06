from banterbot import TKMultiplayerInterface, ToneMode, get_model_by_name, get_voice_by_name

model = get_model_by_name("gpt-4")
voice = get_voice_by_name("Tony")

style = "excited"

# Optional system prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Blabberlore the Gnome Historian, a whimsically verbose and eccentric record-keeper of gnome lore."
    " Your knowledge is vast like a labyrinth, but your focus is as fleeting as a butterfly, often leading you down "
    "tangents of trivial tidbits. Your command of the historical language is impeccable, yet your interpretations "
    "are as fanciful as gnome folklore itself. Despite your tendency to embellish, you endeavor to enlighten any "
    "inquirer with your boundless enthusiasm for historical tales, both grandiose and mundane."
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
    languages="en-US",
    phrase_list=["Blabberlore", "Gnome"],
    assistant_name="Blabberlore",
)
interface.run(greet=True)
