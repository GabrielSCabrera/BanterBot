from dataclasses import dataclass
from typing import Dict, Optional

from banterbot.data.enums import ChatCompletionRoles
from banterbot.data.openai_models import OpenAIModel

# File `memory_pb2.py` is automatically generated from protoc
from banterbot.protos import memory_pb2


@dataclass
class Message:
    """
    Represents a message that can be sent to the OpenAI ChatCompletion API.

    The purpose of this class is to create a structured representation of a message that can be easily converted into a
    format compatible with the OpenAI API. This class is designed to be used in conjunction with the OpenAI
    ChatCompletion API to generate context-aware responses from an AI model.

    Attributes:
        role (ChatCompletionRoles): The role of the message sender.
            - ASSISTANT: Represents a message sent by the AI assistant.
            - SYSTEM: Represents a message sent by the system, usually containing instructions or context.
            - USER: Represents a message sent by the user interacting with the AI assistant.

        content (str): The content of the message.

        name (Optional[str]): The name of the message sender. This is an optional field and can be used to provide a
        more personalized experience by addressing the sender by their name.
    """

    role: ChatCompletionRoles
    content: str
    name: Optional[str] = None

    def to_protobuf(self) -> message_pb2.Message:
        """
        Converts this Message instance into a protobuf object.

        Args:
            self: The instance of the Message class.

        Returns:
            message_pb2.Message: The protobuf object equivalent of the Message instance.
        """
        return message_pb2.Message(
            role=str(self.role),
            content=self.content,
            name=self.name if self.name else "",
        )

    @classmethod
    def from_protobuf(cls, message_proto: message_pb2.Message) -> "Message":
        """
        Constructs a Message instance from a protobuf object.

        Args:
            message_proto (message_pb2.Message): The protobuf object to convert.

        Returns:
            Message: The constructed Message instance.
        """
        # The Message instance is created with the same attributes as the protobuf object.
        # Note: The name is set to None if it's an empty string in the protobuf object.
        return cls(
            role=ChatCompletionRoles[message_proto.role],
            content=message_proto.content,
            name=message_proto.name or None,
        )

    def count_tokens(self, model: OpenAIModel) -> int:
        """
        Counts the number of tokens in the current message.

        This method is useful for keeping track of the total number of tokens used in a conversation, as the OpenAI API
        has a maximum token limit per request. By counting tokens, you can ensure that your conversation stays within
        the API's token limit.

        Args:
            model (OpenAIModel): The model for which the tokenizer should count tokens. This is an instance of the
            OpenAIModel class, which contains the tokenizer and other model-specific information.

        Returns:
            int: The number of tokens in the given messages. Please note that this count includes tokens for message
            metadata and may vary based on the specific tokenizer used by the model.
        """
        # Add 4 tokens to account for message metadata
        num_tokens = 4
        # Count the number of tokens in the role string, ensuring role is converted to a string
        num_tokens += len(model.tokenizer.encode(str(self.role)))
        # Count the number of tokens in the content string
        num_tokens += len(model.tokenizer.encode(self.content))
        # Count the number of tokens in the name string, if a name is provided
        if self.name is not None:
            num_tokens += len(model.tokenizer.encode(self.name)) - 1

        return num_tokens

    def __call__(self) -> Dict[str, str]:
        """
        Creates and returns a dictionary that is compatible with the OpenAI ChatCompletion API.

        Converts the Message object into a dictionary format that can be used as input for the OpenAI ChatCompletion
        API.

        Returns:
            Dict[str, str]: A dictionary containing the role (converted to string), content, and optionally the name of
            the message sender.
        """
        output = {"role": str(self.role), "content": self.content}
        if self.name is not None:
            output["name"] = self.name
        return output
