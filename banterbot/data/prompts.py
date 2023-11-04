from enum import Enum

from banterbot.data import azure_neural_voices

class Greetings(Enum):

    UNPROMPTED_GREETING = "Briefly greet the user or users, according to the parameters provided."

class OptionPredictorPrompts(Enum):

    PREFIX = (
        "Your task is to format the data with the assigned probabilities without providing any comments. The output "
        "must follow the exact format below, without deviation:"
    )

    PROB_VAR = "N"

    SUFFIX = f"Here, {PROB_VAR} represents an integer ranging from 0 to 100."

    DUMMY = "Here is my best attempt at assigning probabilities to the provided items:"


class OptionSelectorPrompts(Enum):

    PREFIX = (
        "Your task is to select the most suitable option from the provided items. Once you have made a decision, "
        "provide the chosen option's index without any additional comments.\nOptions: "
    )

    DUMMY = "Given the current state of the conversation, I expect the assistant to respond with tone number "


class ToneSelection(Enum):

    SYSTEM = (
        "You are an Emotional Tone Evaluator. Given conversational context, you analyze and select the most "
        "appropriate tone/emotion that the assistant is likely to use next. Take into consideration the "
        "conversational context and the assistant's default tone/emotion, which is {}. Make sure to give extra weight "
        "to the default tone/emotion."
    )

    PROMPT = "Choose the most suitable tone/emotion for the assistant's upcoming response."


class ProsodySelection(Enum):

    styles_smallest_set = [
        "angry",
        "cheerful",
        "excited",
        "friendly",
        "hopeful",
        "sad",
        "shouting",
        "terrified",
        "unfriendly",
        "whispering",
    ]
    style_degrees = ["x-weak", "weak", "default", "strong", "x-strong"]
    pitches = ["x-low", "low", "default", "high", "x-high"]
    rates = ["x-slow", "slow", "default", "fast", "x-fast"]
    emphases = ["reduced", "none", "moderate", "strong"]

    styles_smallest_set_str = "\n".join([f"{n+1:02d} {i}" for n, i in enumerate(styles_smallest_set)])
    style_degrees_str = "\n".join([f"{n+1} {i}" for n, i in enumerate(style_degrees)])
    pitches_str = "\n".join([f"{n+1} {i}" for n, i in enumerate(pitches)])
    rates_str = "\n".join([f"{n+1} {i}" for n, i in enumerate(rates)])
    emphases_str = "\n".join([f"{n+1} {i}" for n, i in enumerate(emphases)])

    prefix = (
        "Task: Analyze the context of a set of sentences and assign a specific set of prosody values to each sub-"
        "sentence in the text for a text-to-speech engine that is attempting to mimic human speech patterns. The "
        "parameters are style, style-degree, pitch, rate, and emphasis:"
    )

    style_prompt = (
        '1. "Style": Represents the emotion or tone of the sub-sentence, reflecting the speaker\'s feelings or '
        "attitude. Chosen based on the conversation's context and intended emotion (this value should change once in "
        f"a while). Available styles are:\n{styles_smallest_set_str}"
    )

    style_degrees_prompt = (
        '2. "Style Degree": Indicates the intensity of the style, showing how strongly the speaker feels the emotion:\n'
        f"{style_degrees_str}"
    )

    pitches_prompt = f'3. "Pitch": Sets the voice pitch for a sub-sentence:\n{pitches_str}'
    rates_prompt = f'4. "Rate": Controls the speech speed:\n{rates_str}'

    emphases_prompt = (
        '5. "Emphasis": Assigns relative emphasis to a sub-sentence, highlighting importance. Higher values should be '
        f"assigned to the more important parts of each input (this value should change very often):{emphases_str}"
    )

    suffix = (
        "Your task is to use the conversational context to select the most appropriate combination of these parameters "
        "for each word in order to mimic the speech patterns of actual people. "
        "Make sure each sub-sentence has an individually tailored array, meaning there should be some variation across "
        "the entirety of the output. "
        "The output should be in the following format for each word (there are no spaces between the numbers):\n"
        "[style style-degree pitch rate emphasis] sub-sentence"
    )

    example = (
        "Example:\n"
        "Input:\n"
        "Oh my gosh,\n"
        "I can't believe it!\n"
        "I won the lottery!\n"
        "But,\n"
        "what if people start asking me for money?\n"
        "I'm terrified.\n"
        "Output:\n"
        "034663 Oh my gosh,\n"
        "035454 I can't believe it!\n"
        "035664 I won the lottery!\n"
        "092321 But,\n"
        "092224 what if people start asking me for money?\n"
        "082123 I'm terrified.\n"
    )

    SYSTEM = "\n".join(
        [prefix, style_prompt, style_degrees_prompt, pitches_prompt, rates_prompt, emphases_prompt, suffix, example]
    )


class TextToSpeechPreprocessing(Enum):

    SYSTEM = (
        "You are a text-to-speech preprocessing assistant that converts text generated by a GPT model into a format "
        "that is more easily spoken by a text-to-speech model. Your task is to remove extraneous letters, hyphens, and "
        "correct unconventional spellings to prevent issues where the text-to-speech model misinterprets "
        "pronunciations. You should maintain the original style and intent of the text, only modifying elements that "
        "would cause pronunciation issues."
    )

    EXAMPLE_1 = (
        "Example 1:\n"
        "Input: WHOOOAH! THAT'S A HU-GE DIS-CO-VERY! IT'S LIKE FINDING A NEED-LE IN A HAY-ST-ACK. YOU'VE DONE A "
        "STEL-LAR JOB, PAL! KEEP UP THE GOOD WORK AND DON'T LET THE NAYSAY-ERS GET YOU DOWN.\n"
        "Output: Whoa! That's a huge discovery! It's like finding a needle in a haystack. You've done a stellar job, "
        "pal! Keep up the good work and don't let the naysayers get you down."
    )

    EXAMPLE_2 = (
        "Example 2:\n"
        "Input: H3Y DUDE! I JST R3AD THS AW3SOME B00K ABT A SUP3R-HERO. 1T WAS TOTALLY M1ND-BL0W1NG! THE 3XPL0S1ONS, "
        "F1GHTS, AND P0W3RFUL AB1L1T1ES W3R3 S1CK! I C@N'T W@1T TO SH@R3 1T W1TH MY FR13NDS. THEY'LL B3 TOT@LLY "
        "STOK3D!\n"
        "Output: Hey dude! I just read this awesome book about a superhero. It was totally mind-blowing! The "
        "explosions, fights, and powerful abilities were sick! I can't wait to share it with my friends. They'll be "
        "totally stoked!"
    )
