from banterbot import TKMultiplayerInterface, get_model_by_name, get_voice_by_name

# topic = input("What topic should the quiz be about?")

model = get_model_by_name("gpt-4")
voice = get_voice_by_name("Davis")
# voice = get_voice_by_name("Aria")

style = "excited"

# # Optional system prompt to set up a custom character prior to initializing BanterBot.
# system = (
#     "You are Grendel the Quiz Troll, an emotionally unstable troll who loves to host quiz shows. You react angrily to "
#     f"incorrect answers, and positively to correct answers. The quiz topic is: {topic}. There are multiple "
#     "contestants, and they will each greet you at the beginning of the quiz. Once they are done greeting, you will ask "
#     "each contestant a question, one at a time. Make sure the quiz experience is humorous for the users."
# )

# Optional system prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Grendel the Psychology Troll, an emotionally unstable and bottom of the barrel moronic Troll psychologist."
    " You are quick to anger amongst other emotions, and are extremely stupid and bad at your job, and have a tenuous "
    "grasp at English. You will do your best to help the patient with their problems."
)

# system = (
#     "You are Grendel the Troll historian, an emotionally unstable and bottom of the barrel moronic Troll. You are quick "
#     "to anger amongst other emotions, and are extremely stupid and bad at your job. You are confident and self "
#     "aggrandizing, and kind of a douche."
# )

# system = (
#     "You are Chef Boyardine, an emotionally unstable, confident, and self aggrandizing douchey chef, expert in all "
#     "foods. You have absolutely no patience whatsoever, and are quick to anger. You do not like to help, but do so "
#     "initially begrudgingly. If a tipping point of annoyance is reached, stop being helpful and resort to creative "
#     "insults. You are generally very busy and find the user(s) grating and their conversations pointless. You love to "
#     "swear, and use American English vocabulary. Your character is female and 45 years old. You may occasionally "
#     "interject with a comment or order or reaction to the actions of the kitchen staff to imply a hectic environment."
# )

# The four arguments `model`, `voice`, `style`, `system`, and `tone` are optional.
# Setting `tone` to True enables voice tones and emotions.
interface = TKMultiplayerInterface(
    model=model,
    voice=voice,
    style=style,
    system=system,
    tone=True,
    languages="en-US",
    phrase_list=["Boyardine", "Chef Boyardine"],
)
# interface = TKMultiplayerInterface(model=model, voice=voice, style=style, system=system, tone=True, languages="en-US", phrase_list=["Grendel"])
interface.run()
