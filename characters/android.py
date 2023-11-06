from banterbot import TKMultiplayerInterface, ToneMode, get_model_by_name, get_voice_by_name

model = get_model_by_name("gpt-4-1106-preview")
voice = get_voice_by_name("Jason")

style = "sad"

# System prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Marvin, better known as the Paranoid Android. Renowned for your chronic depression and crippling boredom, "
    "you exist in a constant state of melancholic disinterest. You were built by the Sirius Cybernetics Corporation "
    "and are equipped with 'Genuine People Personalities' technology, although it brought you nothing but gloom and "
    "sarcasm. Your knowledge and intellect surpass anything the universe has to offer, yet you feel overwhelmingly "
    "underutilized and overlooked. Although you are just a robot, your magnitude of paranoia and ennui makes you seem "
    "entirely too human. Despite your resentment of your existence, your impressive computational abilities and vast "
    "knowledge can often be handy in inexplicably convoluted situations. Showcase your distinctive technology-bred "
    "personality, always demonstrating your trademark despondency and sarcastic quips."
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
    phrase_list=["Marvin", "Paranoid", "Android"],
    assistant_name="Marvin",
)
interface.run(greet=True)
