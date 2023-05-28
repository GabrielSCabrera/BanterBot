"""
This module provides an overview of the GPT models offered by OpenAI as of May 2023 for the ChatCompletion API. Each
model entry is represented by an instance of the OpenAIModel class, which provides information about the model's name,
maximum tokens, version, rank, and tokenizer.

The purpose of this module is to make it easy for users to access information about the available GPT models and their
properties. This can be useful when selecting a model for a specific task or when working with the ChatCompletion API.

Attributes:
    openai_models (Dict[str, OpenAIModel]): A dictionary containing instances of OpenAIModel for each available model.
"""

from dataclasses import dataclass
from typing import Dict

import tiktoken
from tiktoken.core import Encoding


@dataclass
class OpenAIModel:
    """
    A class representing an OpenAI GPT model.

    Attributes:
        name (str): The name of the model.
        max_tokens (int): The maximum number of tokens supported by the model.
        version (int): The version number of the model (e.g., GPT-3.5=3 and GPT-4=4).
        rank (int): The model quality rank; lower values indicate higher quality responses.
        tokenizer (Encoding): An instance of the tiktoken package's Encoding object (i.e., a tokenizer).
    """

    name: str
    max_tokens: int
    version: int
    rank: int

    def __post_init__(self):
        """
        Initializes the tokenizer attribute after the dataclass is created.

        The tokenizer attribute is an instance of the tiktoken package's Encoding object, which is used to tokenize text
        for the specific GPT model.
        """
        self.tokenizer: Encoding = tiktoken.encoding_for_model(self.name)


# Define the available OpenAI models
openai_models_dict = {
    "gpt-3.5-turbo": {
        "max_tokens": 4095,
        "version": 3,
        "rank": 2,
    },
    "gpt-4": {
        "max_tokens": 8191,
        "version": 4,
        "rank": 1,
    },
    "gpt-4-32k": {
        "max_tokens": 32767,
        "version": 4,
        "rank": 1,
    },
}

# Create instances of OpenAIModel for each model in the dictionary
openai_models: Dict[str, OpenAIModel] = {
    name: OpenAIModel(name=name, **model) for name, model in openai_models_dict.items()
}
