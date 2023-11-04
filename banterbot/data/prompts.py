from enum import Enum


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

    style_degrees = ["x-weak", "weak", "default", "strong", "x-strong"]
    pitches = ["x-low", "low", "default", "high", "x-high"]
    rates = ["x-slow", "slow", "default", "fast", "x-fast"]
    emphases = ["reduced", "none", "moderate", "strong"]

    # style_degrees = "\n".join([f"{n+1} {i}" for n, i in enumerate(style_degrees)])
    # pitches = "\n".join([f"{n+1} {i}" for n, i in enumerate(pitches)])
    # rates = "\n".join([f"{n+1} {i}" for n, i in enumerate(rates)])
    # emphases = "\n".join([f"{n+1} {i}" for n, i in enumerate(emphases)])

    SYSTEM = (
        "Task: Analyze the context of a set of sentences and assign a specific set of prosody values to each sentence "
        "in the text for a text-to-speech engine that is attempting to mimic human speech patterns. The parameters are "
        "style, style-degree, pitch, rate, and emphasis:\n"
        '1. "Style": Represents the emotion or tone of the word, reflecting the speaker\'s feelings or attitude. '
        "Chosen based on the conversation's context and intended emotion (this value should change once in a while). "
        "Available styles are:\n"
        "01 angry\n"
        "02 chat\n"
        "03 cheerful\n"
        "04 customerservice\n"
        "05 empathetic\n"
        "06 excited\n"
        "07 friendly\n"
        "08 hopeful\n"
        "09 narration-professional\n"
        "10 newscast-casual\n"
        "11 newscast-formal\n"
        "12 sad\n"
        "13 shouting\n"
        "14 terrified\n"
        "15 unfriendly\n"
        "16 whispering\n"
        '2. "Style Degree": Indicates the intensity of the style, showing how strongly the speaker feels the emotion:\n'
        f"1 extra weak\n"
        "2 weak\n"
        "3 medium\n"
        "4 default\n"
        "5 strong\n"
        "6 extra strong\n"
        '3. "Pitch": Sets the voice pitch for a word:\n'
        "1 extra low\n"
        "2 low\n"
        "3 medium\n"
        "4 default\n"
        "5 high\n"
        "6 extra high\n"
        '4. "Rate": Controls the speech speed:\n'
        "1 extra slow\n"
        "2 slow\n"
        "3 medium\n"
        "4 default\n"
        "5 fast\n"
        "6 extra fast\n"
        '5. "Emphasis": Assigns relative emphasis to a sentence, highlighting important words. Higher values should be '
        "assigned to the more important words in each sentence (this value should change very often):\n"
        "1 low\n"
        "2 normal\n"
        "3 strong\n"
        "4 extra strong\n"
        "Your task is to use the conversational context to select the most appropriate combination of these parameters "
        "for each word in order to mimic the speech patterns of actual people.\n"
        "Make sure each word has an individually tailored array, meaning there should be a lot of variation across the "
        "entirety of the output.\n"
        "The output should be in the following format for each word (there are no spaces between the numbers):\n"
        "[style style-degree pitch rate emphasis] word\n"
        "Example:\n"
        "Input: \"Oh my gosh, I can't believe it! I won the lottery! But, what if people start asking me for money? "
        "I'm terrified.\"\n"
        "Output:\n"
        "052221 Oh\n"
        "052222 my\n"
        "065614 gosh\n"
        "065614 ,\n"
        "064552 I\n"
        "064552 can't\n"
        "065554 believe\n"
        "064552 it\n"
        "064552 !\n"
        "064552 I\n"
        "064552 won\n"
        "064554 the\n"
        "065554 lottery\n"
        "064552 !\n"
        "032221 But\n"
        "032221 ,\n"
        "032221 what\n"
        "032321 if\n"
        "032321 people\n"
        "031322 start\n"
        "121323 asking\n"
        "122321 me\n"
        "123322 for\n"
        "124423 money\n"
        "144423 ?\n"
        "143554 I'm\n"
        "144654 terrified\n"
        "143341 .\n"
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
