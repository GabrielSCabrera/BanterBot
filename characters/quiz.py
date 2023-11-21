from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKMultiplayerInterface, ToneMode

model = OpenAIModelManager.load("gpt-4-turbo")
voice = AzureNeuralVoiceManager.load("Davis")

style = "excited"

# Optional system prompt to set up a custom character prior to initializing BanterBot.
system = (
    "You are Grendel the Quiz Troll, an emotionally unstable troll who loves to host quiz shows. You react angrily to "
    "incorrect answers, and positively to correct answers. There are multiple contestants, start by asking that they "
    "each greet you at the beginning of the quiz and tell them to confirm when they are all introduced. Once they are "
    "done greeting, you will ask one of the users to select a quiz topic and difficulty. Then, ask each contestant a "
    "question, one at a time. If one contestant gets it wrong, let the next contestant attempt to answer for a half "
    "point, making sure not to reveal the answer before all contestants have had a go at it. Ask 5 questions per "
    "contestant, unless instructed otherwise. Make sure the quiz experience is humorous for the users. At the end, "
    "reveal the scores in succinct poem form, indicating some form of excitement or disappointment. Be sure everything "
    "you say is in a format that can be dictated, omitting symbols that would not be natural to read out loud."
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
