"""
An overview of the GPT models offered by OpenAI as of May 2023 for the ChatCompletion API. Each model entry is
represented by an instance of the OpenAIModel class, which provides the following information:

Attributes:
    name (str): The name of the model.
    max_tokens (int): The maximum number of tokens supported by the model.
    version (int): The version number of the model (e.g., GPT-3.5=3 and GPT-4=4).
    rank (int): The model quality rank; lower values indicate higher quality responses.
    tokenizer (tiktoken.core.Encoding): An instance of the tiktoken package's Encoding object (i.e., a tokenizer).
"""
from dataclasses import dataclass

import tiktoken


@dataclass
class OpenAIModel:
    name: str
    max_tokens: int
    version: int
    rank: int

    def __post_init__(self):
        self.tokenizer: tiktoken.core.Encoding = tiktoken.encoding_for_model(self.name)


# Define the available OpenAI models
openai_models = {
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
        "version": 3,
        "rank": 2,
    },
    "gpt-4": {
        "max_tokens": 8192,
        "version": 4,
        "rank": 1,
    },
    "gpt-4-32k": {
        "max_tokens": 32768,
        "version": 4,
        "rank": 1,
    },
}

# Create instances of OpenAIModel for each model in the dictionary
openai_models = {name: OpenAIModel(name=name, **model) for name, model in openai_models.items()}
