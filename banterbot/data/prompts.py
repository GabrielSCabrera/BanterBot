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
