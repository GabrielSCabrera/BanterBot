from banterbot import BanterBotTK, get_model_by_name, get_voice_by_name

model = get_model_by_name("gpt-3.5-turbo")
voice = get_voice_by_name("Aria")
style = "chat"

app = BanterBotTK(model=model, voice=voice, style=style)
app.run()
