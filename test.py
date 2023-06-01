from banterbot import BanterBotTK, get_voice_by_name, get_model_by_name

model = get_model_by_name("gpt-3.5-turbo")
voice = get_voice_by_name("Aria")
style = "chat"

# The three arguments `model`, `voice`, and `style` are optional.
BBTK = BanterBotTK(model=model, voice=voice, style=style)
BBTK.run()
