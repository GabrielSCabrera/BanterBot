from dataclasses import dataclass
from typing import Literal, Optional

from banterbot.data.constants import ASSISTANT, SYSTEM, USER
from banterbot.data.openai_models import OpenAIModel


@dataclass
class Message:
    """
    Represents a message that can be sent to the OpenAI ChatCompletion or Completion API.

    Attributes:
        role (Literal[ASSISTANT, SYSTEM, USER]): The role of the message sender.
        content (str): The content of the message.
        name (Optional[str]): The name of the message sender.
    """

    role: Literal[ASSISTANT, SYSTEM, USER]
    content: str
    name: Optional[str] = None

    def count_tokens(self, model: OpenAIModel) -> int:
        """
        Counts the number of tokens in the current message.

        Args:
            model (OpenAIModel): The model for which the tokenizer should count tokens.

        Returns:
            int: The number of tokens in the given messages.
        """
        # Add 4 tokens to account for message metadata
        num_tokens = 4
        # Count the number of tokens in the role string
        num_tokens += len(model.tokenizer.encode(self.role))
        # Count the number of tokens in the content string
        num_tokens += len(model.tokenizer.encode(self.content))
        # Count the number of tokens in the name string, if a name is provided
        if self.name is not None:
            num_tokens += len(model.tokenizer.encode(self.name))

        return num_tokens
