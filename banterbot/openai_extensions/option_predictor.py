import re
from typing import Dict, List, Optional

import numpy as np

from banterbot.api_managers.openai_manager import OpenAIManager
from banterbot.data.openai_models import OpenAIModel, get_model_by_name
from banterbot.data.prompts import OptionPredictorPrompts
from banterbot.utils.message import Message


class OptionPredictor(OpenAIManager):
    """
    The OptionPredictor class is a specialized subclass of OpenAIManager that facilitates evaluating and assigning
    probabilities to a set of provided options given a conversational context.

    This class enhances the capabilities of the base OpenAIManager by providing a mechanism for probability assessment
    for potential responses. The options provided can represent any category or attribute, such as emotional tones,
    topics, sentiment, etc., thus allowing for a variety of uses.

    The class accepts three main parameters: a list of options (strings), a prompt, and an initial system message. The
    system message sets the context for the OptionPredictor's task, while the prompt provides a guideline for the
    evaluation. The probabilities assigned to each option are then produced based on the given conversational context.

    Example: Emotional Tone Prediction

        options = ["angry", "cheerful", "excited", "friendly", "hopeful", "sad", "shouting", "terrified", "unfriendly"]
        prompt = "Analyze the probabilities of different tones/emotions for the assistant's upcoming response."
        system = (
            "You are an Emotional Tone Evaluator. Given conversational context, you analyze and assign probabilities "
            "to a set of tones/emotions that the assistant is likely to use next."
        )

    This example showcases the OptionPredictor as an "Emotional Tone Evaluator". The options are different emotional
    tones. Based on a conversational context, OptionPredictor predicts the likelihood of each tone appearing in the
    assistant's next response.
    """

    def __init__(self, model: OpenAIModel, options: List[str], system: str, prompt: str, seed: Optional[int] = None):
        """
        Initialize the OptionPredictor with the given model, options, system message, and prompt.

        Args:
            model (OpenAIModel): The OpenAI model to be used for generating responses.
            options (List[str]): A list of strings representing the options to be evaluated.
            system (str): The initial system message that sets the context for the OptionPredictor's task.
            prompt (str): The prompt that provides a guideline for the evaluation.
            seed (Optional[int], optional): A seed for the random number generator. Defaults to None.
        """
        super().__init__(model=model)
        self._options = options
        self._system = system
        self._prompt = prompt

        self._system_processed = self._init_system_prompt()
        self._options_patterns = self._compile_options_patterns()

        self._seed = seed
        self._rng = np.random.default_rng(seed=self._seed)

    def _init_system_prompt(self) -> str:
        """
        Initialize the system prompt by combining the system message and the options.

        Returns:
            str: The processed system prompt.
        """
        options = "\n".join(f"{i}: {OptionPredictorPrompts.system_probability_variable}" for i in self._options)
        return f"{OptionPredictorPrompts.system_prefix.value}\n{options}\n{OptionPredictorPrompts.system_suffix.value}"

    def _compile_options_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compile regular expression patterns for each option to extract probabilities from the generated response.

        Returns:
            Dict[str, re.Pattern]: A dictionary mapping options to their corresponding regular expression patterns.
        """
        pattern_format = "^[\W\s]*(?:{})\s*\:\s*(\d+(?:\.\d+)?)"
        patterns = {option: re.compile(pattern_format.format(option)) for option in self._options}
        return patterns

    def _extract_probabilities(self, response: str) -> np.ndarray:
        """
        Extract probabilities for each option from the generated response using the compiled regular expression patterns.

        Args:
            response (str): The generated response from the OpenAI model.

        Returns:
            np.ndarray: A NumPy array containing the probabilities for each option.

        Raises:
            ValueError: If the regular expression search yields no or multiple results for an option.
        """
        probabilities = np.zeros(len(self._options), dtype=np.float64)
        for n, pattern in enumerate(self._options_patterns.values()):
            search = re.findall(pattern=pattern, string=response)
            if not search:
                probability = 0.0
            elif len(search) == 1:
                probability = float(search[0])
            else:
                error_message = (
                    "Class `OptionPredictor` regex search yielded multiple results. Adjust the `options` argument to "
                    "fix this issue."
                )
                raise ValueError(error_message)
            probabilities[n] = probability

        total = np.sum(probabilities)
        if total != 0:
            probabilities = probabilities / total
        else:
            error_message = (
                "Class `OptionPredictor` regex search yielded no results. Adjust the `options` argument to fix this "
                "issue."
            )
            raise ValueError(error_message)
        return probabilities

    def _insert_messages(self, messages: List[Message]) -> List[Message]:
        """
        Insert the system prompt and user prompt into the list of messages.

        Args:
            messages (List[Message]): The list of messages to be processed.

        Returns:
            List[Message]: The updated list of messages with the system prompt and user prompt inserted.
        """
        prefix = Message(role="system", content=self._system_processed)
        suffix = Message(role="user", content=self._prompt)
        messages.insert(0, prefix)
        messages.append(suffix)
        return messages

    def evaluate(self, messages: List[Message]) -> Dict[str, float]:
        """
        Evaluate the probabilities for each option given a list of messages.

        Args:
            messages (List[Message]): The list of messages to be processed.

        Returns:
            Dict[str, float]: A dictionary mapping options to their corresponding probabilities.
        """
        messages = self._insert_messages(messages)
        response = self.prompt(messages=messages, split=False, temperature=0.0, top_p=1.0)
        probabilities = self._extract_probabilities(response=response)
        return {option: probability for option, probability in zip(self._options, probabilities)}

    def random_select(self, messages: List[Message]) -> str:
        """
        Randomly select an option based on the probabilities evaluated for a list of messages.

        Args:
            messages (List[Message]): The list of messages to be processed.

        Returns:
            str: The randomly selected option.
        """
        messages = self._insert_messages(messages)
        response = self.prompt(messages=messages, split=False, temperature=0.0, top_p=1.0)
        probabilities = self._extract_probabilities(response=response)
        return self._rng.choice(self._choices, p=probabilities)
