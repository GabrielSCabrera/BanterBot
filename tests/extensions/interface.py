import unittest
from unittest.mock import patch

from banterbot.data.azure_neural_voices import get_voice_by_name
from banterbot.data.enums import ChatCompletionRoles
from banterbot.data.openai_models import get_model_by_name
from banterbot.extensions.interface import Interface


class MockInterface(Interface):
    def _init_gui(self):
        pass

    def update_conversation_area(self, word: str):
        pass

    def run(self):
        pass


class TestInterface(unittest.TestCase):
    """
    This test suite includes tests for the `Interface` class. It tests the following functionalities:

        1. Sending a message
        2. Prompting the bot
        3. Toggling the listener
        4. Activating the listener
        5. Deactivating the listener

    To avoid making real API calls, the `unittest.mock` library is used to patch the `OpenAIManager` class and other
    methods that interact with external services.
    """

    def setUp(self):
        self.model = get_model_by_name(name="gpt-3.5-turbo")
        self.voice = get_voice_by_name(name="guy")
        self.style = self.voice.styles[0]
        self.interface = MockInterface(model=self.model, voice=self.voice, style=self.style)

    @patch("banterbot.extensions.interface.OpenAIManager")
    def test_send_message(self, mock_openai_manager):
        message = "Hello, how are you?"
        role = ChatCompletionRoles.USER
        name = "John"

        self.interface.send_message(content=message, role=role, name=name)
        self.assertEqual(len(self.interface._messages), 1)
        self.assertEqual(self.interface._messages[0].content, message)
        self.assertEqual(self.interface._messages[0].role, role)
        self.assertEqual(self.interface._messages[0].name, name)

    @patch("banterbot.extensions.interface.OpenAIManager")
    def test_prompt(self, mock_openai_manager):
        message = "Hello, how are you?"
        name = "John"

        with patch.object(self.interface, "send_message") as mock_send_message:
            self.interface.prompt(message=message, name=name)
            mock_send_message.assert_called_once_with(message, ChatCompletionRoles.USER, name)

    @patch("banterbot.extensions.interface.OpenAIManager")
    def test_listener_toggle(self, mock_openai_manager):
        with patch.object(self.interface, "listener_activate") as mock_listener_activate:
            self.interface.listener_toggle()
            mock_listener_activate.assert_called_once()

    @patch("banterbot.extensions.interface.OpenAIManager")
    def test_listener_activate(self, mock_openai_manager):
        name = "John"

        with patch.object(self.interface, "_listen") as mock_listen:
            self.interface.listener_activate(name=name)
            self.assertTrue(self.interface._listening_toggle)
            mock_listen.assert_called_once_with(name)

    @patch("banterbot.extensions.interface.OpenAIManager")
    def test_listener_deactivate(self, mock_openai_manager):
        self.interface._listening_toggle = True
        self.interface.listener_deactivate()
        self.assertFalse(self.interface._listening_toggle)


if __name__ == "__main__":
    unittest.main()
