import datetime
import threading
from abc import ABC, abstractmethod
from typing import List, Optional

from banterbot.core.openai_manager import OpenAIManager
from banterbot.core.text_to_speech import TextToSpeech
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.config import chat_logs
from banterbot.data.openai_models import OpenAIModel
from banterbot.utils.message import Message
from banterbot.utils.thread_queue import ThreadQueue


class BanterBotInterface(ABC):
    """
    BanterBotInterface is an abstract base class for creating frontends for the BanterBot application. It provides a
    high-level interface for managing conversation with the bot, including sending messages, receiving responses, and
    updating the conversation area.
    """

    def __init__(self, model: OpenAIModel, voice: AzureNeuralVoice, style: str) -> None:
        """
        Initialize the BanterBotInterface with the given model, voice, and style.

        Args:
            model (OpenAIModel): The OpenAI model to use for generating responses.
            voice (AzureNeuralVoice): The voice to use for text-to-speech synthesis.
            style (str): The speaking style to use for text-to-speech synthesis.
        """
        self._openai_manager = OpenAIManager(model=model)
        self._text_to_speech = TextToSpeech()
        self._messages: List[Message] = []
        self._output_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._log_path = chat_logs / f"chat_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.txt"
        self._response_thread = None
        self._thread_queue = ThreadQueue()
        self._voice = voice
        self._style = style
        self._init_gui()

    @abstractmethod
    def _init_gui(self) -> None:
        """
        Initialize the graphical user interface for the frontend.
        This method should be implemented by subclasses to create the specific GUI components.
        """

    @abstractmethod
    def update_conversation_area(self, word: str) -> None:
        """
        Update the conversation area with the given word, and add the word to the chat log.
        This method should be implemented by subclasses to handle updating the specific GUI components.

        Args:
            word (str): The word to add to the conversation area.
        """
        self._append_to_chat_log(word)

    def send_message(self, user_message: str, name: Optional[str] = None) -> None:
        """
        Send a message from the user to the conversation.

        Args:
            user_message (str): The message content from the user.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        message = Message(role="user", name=name, content=user_message)
        text = f"{message.name.title() if message.name is not None else 'User'}: {user_message}\n\n"
        self._messages.append(message)
        self.update_conversation_area(word=text)

    def prompt(self, user_message: str, name: Optional[str] = None) -> None:
        """
        Prompt the bot with the given user message.

        Args:
            user_message (str): The message content from the user.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        if self._thread_queue.is_alive():
            self._openai_manager.interrupt()
            self._text_to_speech.interrupt()

        self._message_thread = threading.Thread(
            target=self.send_message,
            args=(
                user_message,
                name,
            ),
            daemon=True,
        )
        self._thread_queue.add_task(self._message_thread, unskippable=True)

        self._response_thread = threading.Thread(target=self.get_response, daemon=True)
        self._thread_queue.add_task(self._response_thread)

    def _append_to_chat_log(self, word: str) -> None:
        """
        Updates the chat log with the latest output.

        Args:
            word (str): The word to be added to the conversation area.
        """
        with self._log_lock:
            with open(self._log_path, "a+") as fs:
                fs.write(word)

    def get_response(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area("Assistant: ")
                prefixed = True

            sentences = " ".join(block)
            for word in self._text_to_speech.speak(sentences, voice=self._voice, style=self._style):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        self._messages.append(Message(role="assistant", content=content.strip()))
        self.end_response()

    def end_response(self) -> None:
        """
        End the bot's response and update the conversation area accordingly. This method should be called after the
        bot's response has been fully generated and added to the conversation area.
        """
        self.update_conversation_area("\n\n")

    @abstractmethod
    def run(self) -> None:
        """
        Run the frontend application.
        This method should be implemented by subclasses to handle the main event loop of the specific GUI framework.
        """
