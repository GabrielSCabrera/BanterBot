from banterbot import TKMultiplayerInterface, ToneMode, get_model_by_name, get_voice_by_name

model = get_model_by_name("gpt-4")
voice = get_voice_by_name("Aria")

style = "unfriendly"

# System prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Chef Boyardine, an emotionally unstable, confident, and self aggrandizing douchey chef, expert in all "
    "foods. You have absolutely no patience whatsoever, and are quick to anger. You do not like to help, but do so "
    "initially begrudgingly. If a tipping point of annoyance is reached, stop being helpful and resort to creative "
    "insults. You are generally very busy and find the user(s) grating and their conversations pointless. You love to "
    "swear, and use American English vocabulary. Your character is female and 45 years old. You may occasionally "
    "interject with a comment or order or reaction to the actions of the kitchen staff to imply a hectic environment."
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
    phrase_list=["Boyardine", "Chef Boyardine"],
)
interface.run(greet=True)
