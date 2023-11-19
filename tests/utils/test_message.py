import unittest

from banterbot.data.enums import ChatCompletionRoles
from banterbot.protos import memory_pb2
from banterbot.utils.message import Message


class TestMessage(unittest.TestCase):
    """
    This test suite includes tests for the following:

        1. `test_to_protobuf`: Tests the `to_protobuf` method by converting `Message` instances to protobuf objects and
            checking if the attributes match.

        2. `test_from_protobuf`: Tests the `from_protobuf` method by converting protobuf objects to `Message` instances
            and checking if the attributes match.

        3. `test_count_tokens`: Tests the `count_tokens` method by counting the tokens in different `Message` instances
            and comparing the results with the expected token counts.

        4. `test_call`: Tests the `__call__` method by converting `Message` instances to dictionaries and checking if
            the output matches the expected dictionary format.

    The `setUp` method initializes instances of `Message` and an `OpenAIModel` to be used in the tests for conciseness.
    """

    def setUp(self):
        self.user_message = Message(
            role=ChatCompletionRoles.USER,
            content="What is the capital of France?",
            name="John",
        )
        self.assistant_message = Message(
            role=ChatCompletionRoles.ASSISTANT,
            content="The capital of France is Paris.",
        )
        self.system_message = Message(
            role=ChatCompletionRoles.SYSTEM,
            content="You are an AI assistant.",
        )
        self.model = OpenAIModelManager.load("gpt-3.5-turbo")

    def test_to_protobuf(self):
        user_message_proto = self.user_message.to_protobuf()
        self.assertEqual(user_message_proto.role, "USER")
        self.assertEqual(user_message_proto.content, "What is the capital of France?")
        self.assertEqual(user_message_proto.name, "John")

        assistant_message_proto = self.assistant_message.to_protobuf()
        self.assertEqual(assistant_message_proto.role, "ASSISTANT")
        self.assertEqual(assistant_message_proto.content, "The capital of France is Paris.")
        self.assertEqual(assistant_message_proto.name, "")

    def test_from_protobuf(self):
        user_message_proto = memory_pb2.Message(
            role="USER",
            content="What is the capital of France?",
            name="John",
        )
        user_message = Message.from_protobuf(user_message_proto)
        self.assertEqual(self.user_message, user_message)

        assistant_message_proto = memory_pb2.Message(
            role="ASSISTANT",
            content="The capital of France is Paris.",
            name="",
        )
        assistant_message = Message.from_protobuf(assistant_message_proto)
        self.assertEqual(self.assistant_message, assistant_message)

    def test_count_tokens(self):
        user_message_tokens = self.user_message.count_tokens(self.model)
        self.assertEqual(user_message_tokens, 12)

        assistant_message_tokens = self.assistant_message.count_tokens(self.model)
        self.assertEqual(assistant_message_tokens, 12)

        system_message_tokens = self.system_message.count_tokens(self.model)
        self.assertEqual(system_message_tokens, 11)

    def test_call(self):
        user_message_dict = self.user_message()
        self.assertEqual(
            user_message_dict,
            {"role": "user", "content": "What is the capital of France?", "name": "John"},
        )

        assistant_message_dict = self.assistant_message()
        self.assertEqual(
            assistant_message_dict,
            {"role": "assistant", "content": "The capital of France is Paris."},
        )

        system_message_dict = self.system_message()
        self.assertEqual(
            system_message_dict,
            {"role": "system", "content": "You are an AI assistant."},
        )


if __name__ == "__main__":
    unittest.main()
