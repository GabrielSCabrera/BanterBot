from enum import Enum


class OptionPredictorPrompts(Enum):

    system_prefix = (
        "Your task is to format the data with the assigned probabilities without providing any comments. The output "
        "should follow the format below:"
    )

    system_probability_variable = "N"

    system_suffix = f"Here, {system_probability_variable} represents an integer ranging from 0 to 100."
