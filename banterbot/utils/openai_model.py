from dataclasses import dataclass

import tiktoken


@dataclass
class OpenAIModel:
    """
    A class representing an OpenAI ChatCompletion model.

    Attributes:
        model (str): The name of the model.
        max_tokens (int): The maximum number of tokens supported by the model.
        generation (int): The generation number of the model (e.g., GPT-3.5=3 and GPT-4=4).
        rank (int): The model quality rank; lower values indicate higher quality responses.
        tokenizer (Encoding): An instance of the tiktoken package's Encoding object (i.e., a tokenizer).
    """

    model: str
    max_tokens: int
    generation: float
    rank: int

    def __post_init__(self):
        """
        Initializes the tokenizer attribute after the dataclass is created.

        The tokenizer attribute is an instance of the tiktoken package's Encoding object, which is used to tokenize text
        for the specific GPT model.
        """
        self.tokenizer: tiktoken.core.Encoding = tiktoken.encoding_for_model(self.model)
